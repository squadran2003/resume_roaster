import io
import logging
import secrets
import uuid as uuid_mod

from django.conf import settings as django_settings
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

from apps.resumes.models import Resume

from .models import AnalysisResult, JobDescription, LinkedInAnalysis
from .serializers import (
    AnalysisCreateSerializer,
    AnalysisResultSerializer,
    LinkedInAnalysisSerializer,
    LinkedInCreateSerializer,
)
from .tasks import run_analysis_task, run_interview_prep_task, run_linkedin_task, run_resume_rewrite_task
from .throttles import AIAnalysisThrottle


class AnalysisCreateView(APIView):
    throttle_classes = [AIAnalysisThrottle]

    def post(self, request):
        serializer = AnalysisCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        resume = get_object_or_404(Resume, id=d["resume_id"], user=request.user)

        # Usage check: skip for staff/superusers
        if not request.user.is_staff:
            if django_settings.PAYMENTS_ENABLED:
                profile = request.user.profile
                if profile.credits_remaining < 1:
                    return Response(
                        {"detail": "No credits remaining. Please purchase more credits."},
                        status=status.HTTP_402_PAYMENT_REQUIRED,
                    )
                updated = type(profile).objects.filter(
                    pk=profile.pk, credits_remaining__gte=1
                ).update(credits_remaining=models.F("credits_remaining") - 1)
                if not updated:
                    return Response(
                        {"detail": "No credits remaining. Please purchase more credits."},
                        status=status.HTTP_402_PAYMENT_REQUIRED,
                    )
                profile.refresh_from_db()
            else:
                allowed, used, limit = _check_daily_limit(request.user)
                if not allowed:
                    return Response(
                        {"detail": f"Daily limit reached ({limit} analyses per 24 hours). Try again later."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )

        job_desc = JobDescription.objects.create(
            user=request.user,
            title=d.get("job_title", ""),
            company=d.get("company", ""),
            raw_text=d["job_description"],
        )

        result = AnalysisResult.objects.create(
            resume=resume,
            job_description=job_desc,
        )

        run_analysis_task.delay(str(result.id))

        return Response(
            AnalysisResultSerializer(result).data,
            status=status.HTTP_202_ACCEPTED,
        )


class AnalysisDetailView(APIView):
    def get(self, request, pk):
        result = get_object_or_404(
            AnalysisResult,
            id=pk,
            resume__user=request.user,
        )
        return Response(AnalysisResultSerializer(result).data)

    def delete(self, request, pk):
        result = get_object_or_404(
            AnalysisResult,
            id=pk,
            resume__user=request.user,
        )
        result.delete()
        return Response(status=204)


class AnalysisListView(APIView):
    """List all analyses for the authenticated user, most recent first."""

    def get(self, request):
        qs = AnalysisResult.objects.filter(
            resume__user=request.user
        ).select_related("job_description", "resume").order_by("-created_at")

        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(qs, request)
        serializer = AnalysisResultSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class AnalysisCompareView(APIView):
    """Return two analyses side-by-side for comparison."""

    def get(self, request):
        ids_param = request.query_params.get("ids", "")
        raw_ids = [x.strip() for x in ids_param.split(",") if x.strip()]

        if len(raw_ids) != 2:
            return Response(
                {"detail": "Provide exactly 2 comma-separated analysis IDs."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            ids = [str(uuid_mod.UUID(i)) for i in raw_ids]
        except ValueError:
            return Response(
                {"detail": "Invalid analysis ID format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = AnalysisResult.objects.filter(
            id__in=ids, resume__user=request.user
        ).select_related("job_description", "resume")

        if results.count() != 2:
            return Response(
                {"detail": "One or both analyses not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AnalysisResultSerializer(results, many=True)
        return Response(serializer.data)


def _get_daily_analysis_count(user):
    """Count analyses created by the user in the last 24 hours."""
    since = timezone.now() - timezone.timedelta(hours=24)
    return AnalysisResult.objects.filter(
        resume__user=user, created_at__gte=since
    ).count() + LinkedInAnalysis.objects.filter(
        user=user, created_at__gte=since
    ).count()


def _check_daily_limit(user):
    """Check if user has exceeded the free daily analysis limit.
    Returns (allowed, used, limit)."""
    limit = django_settings.FREE_DAILY_ANALYSIS_LIMIT
    used = _get_daily_analysis_count(user)
    return used < limit, used, limit


def _check_usage_allowed(user):
    """Check if the user can perform an analysis action.
    Returns (allowed: bool, error_detail: str|None, http_status: int|None).
    Staff/superusers are always allowed."""
    if user.is_staff:
        return True, None, None

    if django_settings.PAYMENTS_ENABLED:
        from apps.accounts.models import Profile

        updated = Profile.objects.filter(
            user=user, credits_remaining__gte=1
        ).update(credits_remaining=models.F("credits_remaining") - 1)
        if not updated:
            return False, "No credits remaining. Please purchase more credits.", status.HTTP_402_PAYMENT_REQUIRED
        return True, None, None
    else:
        allowed, used, limit = _check_daily_limit(user)
        if not allowed:
            return False, f"Daily limit reached ({limit} analyses per 24 hours). Try again later.", status.HTTP_429_TOO_MANY_REQUESTS
        return True, None, None


class ResumeRewriteView(APIView):
    """Trigger a full resume rewrite for an existing analysis. Costs 1 credit."""

    throttle_classes = [AIAnalysisThrottle]

    def post(self, request, pk):
        result = get_object_or_404(
            AnalysisResult, id=pk, resume__user=request.user, status=AnalysisResult.Status.DONE,
        )

        if result.rewritten_resume_text:
            return Response(
                {"detail": "Resume rewrite already generated.", "rewritten_resume_text": result.rewritten_resume_text},
            )

        allowed, detail, http_status = _check_usage_allowed(request.user)
        if not allowed:
            return Response({"detail": detail}, status=http_status)

        run_resume_rewrite_task.delay(str(result.id))
        return Response({"detail": "Resume rewrite started."}, status=status.HTTP_202_ACCEPTED)


class ResumeRewritePDFView(APIView):
    """Download the rewritten resume as a formatted PDF."""

    def get(self, request, pk):
        result = get_object_or_404(
            AnalysisResult, id=pk, resume__user=request.user,
        )

        if not result.rewritten_resume_text and not result.rewritten_resume_json:
            return Response(
                {"detail": "No rewritten resume available. Generate one first."},
                status=status.HTTP_404_NOT_FOUND,
            )

        jd_title = result.job_description.title or "tailored"
        filename = slugify(f"resume-{jd_title}")[:60] + ".pdf"

        # Extract styles from the original resume to match its look
        styles = self._extract_original_styles(result.resume)

        # Use structured JSON path (new rewrites) or fall back to legacy FPDF
        if result.rewritten_resume_json:
            pdf_bytes = self._render_weasyprint(result.rewritten_resume_json, styles)
        else:
            pdf_bytes = self._render_fpdf_legacy(result.rewritten_resume_text)

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Length"] = len(pdf_bytes)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    @staticmethod
    def _extract_original_styles(resume):
        """Extract visual styles from the original uploaded resume."""
        from .style_extractor import (
            default_styles,
            extract_styles_from_docx,
            extract_styles_from_pdf,
        )

        docx_mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        try:
            resume.file.open("rb")
            try:
                if resume.mime_type == docx_mime:
                    return extract_styles_from_docx(resume.file)
                else:
                    return extract_styles_from_pdf(resume.file)
            finally:
                resume.file.close()
        except Exception:
            logger.exception("Could not extract styles from original resume")
            return default_styles()

    def _render_weasyprint(self, data, styles=None):
        """Render structured resume JSON to PDF using fpdf2 (no system deps)."""
        import re

        from fpdf import FPDF

        from .style_extractor import default_styles

        if styles is None:
            styles = default_styles()

        def strip_unsupported(t):
            return re.sub(r'[^\x00-\xFF]', '', t).strip()

        def parse_pt(val):
            """Extract numeric pt value from strings like '10pt' or '0.7in'."""
            if isinstance(val, (int, float)):
                return float(val)
            m = re.match(r'([\d.]+)\s*(pt|in)?', str(val))
            if not m:
                return 10.0
            num = float(m.group(1))
            unit = m.group(2) or 'pt'
            if unit == 'in':
                return num * 72  # convert inches to points
            return num

        def hex_to_rgb(h):
            h = h.lstrip('#')
            if len(h) == 6:
                return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return 34, 34, 34

        # Parse style values
        name_size = parse_pt(styles.get("name_size", "22pt"))
        heading_size = parse_pt(styles.get("heading_size", "11pt"))
        body_size = parse_pt(styles.get("body_size", "10pt"))
        contact_size = parse_pt(styles.get("contact_size", "9pt"))
        margin_top = parse_pt(styles.get("margin_top", "0.6in")) / 72 * 25.4  # to mm
        margin_right = parse_pt(styles.get("margin_right", "0.7in")) / 72 * 25.4
        margin_bottom = parse_pt(styles.get("margin_bottom", "0.6in")) / 72 * 25.4
        margin_left = parse_pt(styles.get("margin_left", "0.7in")) / 72 * 25.4
        line_height = float(styles.get("line_height", "1.35"))

        name_rgb = hex_to_rgb(styles.get("name_color", "#1a1a2e"))
        heading_rgb = hex_to_rgb(styles.get("heading_color", "#1a1a2e"))
        body_rgb = hex_to_rgb(styles.get("body_color", "#222222"))
        contact_rgb = hex_to_rgb(styles.get("contact_color", "#555555"))
        accent_rgb = hex_to_rgb(styles.get("accent_color", "#1a1a2e"))
        subheading_rgb = hex_to_rgb(styles.get("subheading_color", "#555555"))

        heading_border = styles.get("heading_border", True)
        name_align = styles.get("name_align", "center")
        align_map = {"center": "C", "left": "L", "right": "R"}

        pdf_doc = FPDF()
        pdf_doc.set_margins(left=margin_left, top=margin_top, right=margin_right)
        pdf_doc.set_auto_page_break(auto=True, margin=margin_bottom)
        pdf_doc.add_page()

        body_line_h = body_size * line_height * 0.3528  # pt to mm

        # --- Name ---
        name = strip_unsupported(data.get("name", ""))
        if name:
            pdf_doc.set_font("Helvetica", "B", name_size)
            pdf_doc.set_text_color(*name_rgb)
            pdf_doc.cell(0, name_size * 0.4, name, align=align_map.get(name_align, "C"),
                         new_x="LMARGIN", new_y="NEXT")
            pdf_doc.ln(1)

        # --- Contact ---
        contact_parts = [strip_unsupported(p) for p in (data.get("contact") or "").split("|") if p.strip()]
        if contact_parts:
            pdf_doc.set_font("Helvetica", "", contact_size)
            pdf_doc.set_text_color(*contact_rgb)
            contact_line = "  |  ".join(contact_parts)
            pdf_doc.cell(0, contact_size * 0.4, contact_line,
                         align=align_map.get(name_align, "C"),
                         new_x="LMARGIN", new_y="NEXT")
            pdf_doc.ln(4)

        # --- Summary ---
        summary = strip_unsupported(data.get("summary", ""))
        if summary:
            pdf_doc.set_font("Helvetica", "", body_size)
            pdf_doc.set_text_color(*body_rgb)
            pdf_doc.multi_cell(0, body_line_h, summary)
            pdf_doc.ln(3)

        # --- Sections ---
        for section in data.get("sections", []):
            title = strip_unsupported(section.get("title", ""))
            if title:
                pdf_doc.ln(2)
                pdf_doc.set_font("Helvetica", "B", heading_size)
                pdf_doc.set_text_color(*heading_rgb)
                pdf_doc.cell(0, heading_size * 0.45, title.upper(),
                             new_x="LMARGIN", new_y="NEXT")
                if heading_border:
                    pdf_doc.set_draw_color(*accent_rgb)
                    pdf_doc.set_line_width(0.4)
                    y = pdf_doc.get_y()
                    pdf_doc.line(pdf_doc.l_margin, y,
                                 pdf_doc.w - pdf_doc.r_margin, y)
                pdf_doc.ln(2)

            for entry in section.get("entries", []):
                heading = strip_unsupported(entry.get("heading", ""))
                if heading:
                    pdf_doc.set_font("Helvetica", "B", body_size)
                    pdf_doc.set_text_color(*heading_rgb)
                    pdf_doc.cell(0, body_line_h, heading,
                                 new_x="LMARGIN", new_y="NEXT")

                subheading = strip_unsupported(entry.get("subheading", ""))
                if subheading:
                    pdf_doc.set_font("Helvetica", "I", max(8, body_size - 1))
                    pdf_doc.set_text_color(*subheading_rgb)
                    pdf_doc.cell(0, body_line_h, subheading,
                                 new_x="LMARGIN", new_y="NEXT")

                bullets = entry.get("bullets", [])
                if bullets:
                    pdf_doc.set_font("Helvetica", "", body_size)
                    pdf_doc.set_text_color(*body_rgb)
                    for bullet in bullets:
                        cleaned = strip_unsupported(bullet)
                        if not cleaned:
                            continue
                        pdf_doc.set_x(pdf_doc.l_margin + 4)
                        pdf_doc.multi_cell(
                            pdf_doc.w - pdf_doc.l_margin - pdf_doc.r_margin - 4,
                            body_line_h,
                            f"- {cleaned}",
                        )

                pdf_doc.ln(2)

        return bytes(pdf_doc.output())

    def _render_fpdf_legacy(self, text):
        """Fallback for old rewrites that only have plain text."""
        import re

        from fpdf import FPDF

        def strip_unsupported_chars(t):
            return re.sub(r'[^\x00-\xFF]', '', t).strip()

        pdf_doc = FPDF()
        pdf_doc.set_margins(left=15, top=15, right=15)
        pdf_doc.set_auto_page_break(auto=True, margin=20)
        pdf_doc.add_page()
        bullet_indent = 8

        lines = text.split("\n")
        is_first_line = True
        for line in lines:
            stripped = strip_unsupported_chars(line)
            if not stripped:
                pdf_doc.ln(4)
                continue
            if is_first_line:
                pdf_doc.set_font("Helvetica", "B", 16)
                pdf_doc.set_text_color(26, 26, 46)
                pdf_doc.set_x(pdf_doc.l_margin)
                pdf_doc.cell(0, 8, stripped, align="C", new_x="LMARGIN", new_y="NEXT")
                is_first_line = False
            elif stripped.isupper() and len(stripped) < 60:
                pdf_doc.ln(6)
                pdf_doc.set_font("Helvetica", "B", 13)
                pdf_doc.set_text_color(26, 26, 46)
                pdf_doc.set_x(pdf_doc.l_margin)
                pdf_doc.cell(0, 7, stripped, new_x="LMARGIN", new_y="NEXT")
                pdf_doc.set_draw_color(230, 74, 25)
                pdf_doc.set_line_width(0.5)
                y = pdf_doc.get_y()
                pdf_doc.line(pdf_doc.l_margin, y, pdf_doc.w - pdf_doc.r_margin, y)
                pdf_doc.ln(3)
            elif stripped.startswith("- ") or stripped.startswith("* "):
                pdf_doc.set_font("Helvetica", "", 10)
                pdf_doc.set_text_color(34, 34, 34)
                pdf_doc.set_x(pdf_doc.l_margin + bullet_indent)
                pdf_doc.multi_cell(0, 5, f"- {stripped[2:]}")
            else:
                pdf_doc.set_font("Helvetica", "", 10)
                pdf_doc.set_text_color(34, 34, 34)
                pdf_doc.set_x(pdf_doc.l_margin)
                pdf_doc.multi_cell(0, 5, stripped)

        return bytes(pdf_doc.output())


class ResumeRewriteDOCXView(APIView):
    """Download the rewritten resume as a DOCX preserving original formatting."""

    def get(self, request, pk):
        result = get_object_or_404(
            AnalysisResult, id=pk, resume__user=request.user,
        )

        if not result.rewritten_resume_json:
            return Response(
                {"detail": "No structured rewrite available."},
                status=status.HTTP_404_NOT_FOUND,
            )

        docx_mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if result.resume.mime_type != docx_mime:
            return Response(
                {"detail": "Original resume was not a DOCX file. Use the PDF download instead."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from .docx_rewriter import rewrite_docx_preserving_format

        result.resume.file.open("rb")
        try:
            docx_bytes = rewrite_docx_preserving_format(
                result.resume.file, result.rewritten_resume_json,
            )
        finally:
            result.resume.file.close()

        jd_title = result.job_description.title or "tailored"
        filename = slugify(f"resume-{jd_title}")[:60] + ".docx"

        response = HttpResponse(docx_bytes, content_type=docx_mime)
        response["Content-Length"] = len(docx_bytes)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class InterviewPrepView(APIView):
    """Generate interview prep questions for an existing analysis. Costs 1 credit."""

    throttle_classes = [AIAnalysisThrottle]

    def post(self, request, pk):
        result = get_object_or_404(
            AnalysisResult, id=pk, resume__user=request.user, status=AnalysisResult.Status.DONE,
        )

        if result.interview_questions:
            return Response(
                {"detail": "Interview questions already generated.", "interview_questions": result.interview_questions},
            )

        allowed, detail, http_status = _check_usage_allowed(request.user)
        if not allowed:
            return Response({"detail": detail}, status=http_status)

        # Clear any previous error so polling can detect new failures
        if result.error_message:
            result.error_message = ""
            result.save(update_fields=["error_message"])

        run_interview_prep_task.delay(str(result.id))
        return Response({"detail": "Interview prep generation started."}, status=status.HTTP_202_ACCEPTED)


class LinkedInAnalyzeView(APIView):
    """Analyze and optimize LinkedIn profile sections. Costs 1 credit."""

    throttle_classes = [AIAnalysisThrottle]

    def post(self, request):
        serializer = LinkedInCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        allowed, detail, http_status = _check_usage_allowed(request.user)
        if not allowed:
            return Response({"detail": detail}, status=http_status)

        obj = LinkedInAnalysis.objects.create(
            user=request.user,
            headline=d["headline"],
            about=d["about"],
            jd_text=d["jd_text"],
        )

        run_linkedin_task.delay(str(obj.id))
        return Response(
            LinkedInAnalysisSerializer(obj).data,
            status=status.HTTP_202_ACCEPTED,
        )


class LinkedInDetailView(APIView):
    def get(self, request, pk):
        obj = get_object_or_404(LinkedInAnalysis, id=pk, user=request.user)
        return Response(LinkedInAnalysisSerializer(obj).data)


class ShareTokenView(APIView):
    """Generate or retrieve a share token for an analysis."""

    def post(self, request, pk):
        result = get_object_or_404(
            AnalysisResult, id=pk, resume__user=request.user, status=AnalysisResult.Status.DONE,
        )
        if not result.share_token:
            result.share_token = secrets.token_urlsafe(16)
            result.save(update_fields=["share_token"])
        return Response({"share_token": result.share_token})


class PublicShareView(APIView):
    """Public endpoint returning limited analysis data for a shared score card."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, token):
        result = get_object_or_404(
            AnalysisResult, share_token=token, status=AnalysisResult.Status.DONE,
        )
        keyword_matches = result.keyword_matches or []
        found = sum(1 for k in keyword_matches if k.get("found"))
        data = {
            "match_score": result.match_score,
            "hire_probability": result.hire_probability,
            "job_title": result.job_description.title,
            "company": result.job_description.company,
            "keywords_found": found,
            "keywords_total": len(keyword_matches),
            "ats_issues": len(result.ats_flags or []),
            "created_at": result.created_at,
            "payments_enabled": django_settings.PAYMENTS_ENABLED,
        }
        return Response(data)


class ScoreCardImageView(APIView):
    """Generate a branded PNG score card image for social sharing. Public endpoint."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, token):
        result = get_object_or_404(
            AnalysisResult, share_token=token, status=AnalysisResult.Status.DONE,
        )

        from PIL import Image, ImageDraw, ImageFont

        W, H = 1200, 630
        img = Image.new("RGB", (W, H), "#0d0d1a")
        draw = ImageDraw.Draw(img)

        # Fonts — try common paths (Debian, Nix, fallback)
        def _find_font(name):
            import subprocess
            # Try fc-match first (works on both Debian and Nix with fontconfig)
            try:
                out = subprocess.run(
                    ["fc-match", "-f", "%{file}", name],
                    capture_output=True, text=True, timeout=5,
                )
                if out.returncode == 0 and out.stdout.strip():
                    return out.stdout.strip()
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
            # Fallback to common Debian paths
            import os
            for prefix in ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/TTF"]:
                path = os.path.join(prefix, name)
                if os.path.isfile(path):
                    return path
            return None

        bold_path = _find_font("DejaVuSans-Bold.ttf")
        regular_path = _find_font("DejaVuSans.ttf")
        try:
            font_lg = ImageFont.truetype(bold_path or "DejaVuSans-Bold", 72)
            font_md = ImageFont.truetype(bold_path or "DejaVuSans-Bold", 36)
            font_sm = ImageFont.truetype(regular_path or "DejaVuSans", 28)
            font_xs = ImageFont.truetype(regular_path or "DejaVuSans", 22)
        except OSError:
            font_lg = ImageFont.load_default()
            font_md = font_lg
            font_sm = font_lg
            font_xs = font_lg

        # Background gradient effect — draw colored rectangles
        for i in range(H):
            r = int(13 + (15 * i / H))
            g = int(13 + (52 * i / H))
            b = int(26 + (96 * i / H))
            draw.line([(0, i), (W, i)], fill=(r, g, b))

        # Score circle
        score = result.match_score or 0
        cx, cy, radius = 300, 280, 120
        if score >= 75:
            score_color = "#4CAF50"
        elif score >= 50:
            score_color = "#FF9800"
        else:
            score_color = "#F44336"

        # Draw circle background
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            outline="#ffffff30", width=8,
        )
        # Draw score arc
        arc_end = int(score * 3.6) - 90
        draw.arc(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            start=-90, end=arc_end, fill=score_color, width=12,
        )
        # Score text
        score_text = str(score)
        bbox = draw.textbbox((0, 0), score_text, font=font_lg)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((cx - tw // 2, cy - th // 2 - 10), score_text, fill="white", font=font_lg)
        # "/100" below
        bbox2 = draw.textbbox((0, 0), "/100", font=font_sm)
        tw2 = bbox2[2] - bbox2[0]
        draw.text((cx - tw2 // 2, cy + th // 2 + 5), "/100", fill="#ffffff99", font=font_sm)

        # Right side info
        rx = 520
        # Title
        draw.text((rx, 100), "Resume Roaster", fill="#E64A19", font=font_md)
        draw.text((rx, 150), "AI Resume Analysis", fill="#ffffff99", font=font_xs)

        # Job info
        job_title = result.job_description.title or "Job Position"
        company = result.job_description.company
        job_line = job_title[:40]
        if company:
            job_line += f" @ {company[:25]}"
        draw.text((rx, 220), job_line, fill="white", font=font_sm)

        # Stats
        hire_pct = int((result.hire_probability or 0) * 100)
        keyword_matches = result.keyword_matches or []
        found = sum(1 for k in keyword_matches if k.get("found"))
        total = len(keyword_matches)
        ats_count = len(result.ats_flags or [])

        stats = [
            (f"Hire Probability: {hire_pct}%", "#4CAF50" if hire_pct >= 60 else "#FF9800" if hire_pct >= 35 else "#F44336"),
            (f"Keywords: {found}/{total} matched", "#4CAF50" if total and found / total >= 0.7 else "#FF9800"),
            (f"ATS Issues: {ats_count}", "#4CAF50" if ats_count == 0 else "#FF9800"),
        ]
        for i, (text, color) in enumerate(stats):
            y = 290 + i * 50
            draw.rounded_rectangle([rx, y, rx + 16, y + 28], radius=4, fill=color)
            draw.text((rx + 28, y - 2), text, fill="white", font=font_xs)

        # CTA
        draw.text((rx, 480), "Roast your resume too!", fill="#E64A19", font=font_md)
        draw.text((rx, 530), "resume-roaster.com", fill="#ffffff80", font=font_xs)

        # Fire emoji placeholder (orange circle)
        draw.ellipse([50, 50, 90, 90], fill="#E64A19")
        draw.text((100, 52), "Resume Roaster", fill="white", font=font_md)

        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        buf.seek(0)

        response = HttpResponse(buf.read(), content_type="image/png")
        response["Content-Length"] = buf.tell()
        response["Cache-Control"] = "public, max-age=86400"
        return response
