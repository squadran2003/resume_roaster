import logging
import uuid as uuid_mod

from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
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

        # Credit check: staff bypass, otherwise deduct 1 credit
        profile = request.user.profile
        if not request.user.is_staff:
            if profile.credits_remaining < 1:
                return Response(
                    {"detail": "No credits remaining. Please purchase more credits."},
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )
            # Atomically deduct credit
            updated = type(profile).objects.filter(
                pk=profile.pk, credits_remaining__gte=1
            ).update(credits_remaining=models.F("credits_remaining") - 1)
            if not updated:
                return Response(
                    {"detail": "No credits remaining. Please purchase more credits."},
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )
            profile.refresh_from_db()

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


def _deduct_credit(user):
    """Atomically deduct 1 credit. Returns True on success, False if insufficient."""
    from apps.accounts.models import Profile

    updated = Profile.objects.filter(
        user=user, credits_remaining__gte=1
    ).update(credits_remaining=models.F("credits_remaining") - 1)
    return bool(updated)


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

        if not request.user.is_staff and not _deduct_credit(request.user):
            return Response(
                {"detail": "No credits remaining. Please purchase more credits."},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        run_resume_rewrite_task.delay(str(result.id))
        return Response({"detail": "Resume rewrite started."}, status=status.HTTP_202_ACCEPTED)


class ResumeRewritePDFView(APIView):
    """Download the rewritten resume as a formatted PDF."""

    def get(self, request, pk):
        result = get_object_or_404(
            AnalysisResult, id=pk, resume__user=request.user,
        )

        if not result.rewritten_resume_text:
            return Response(
                {"detail": "No rewritten resume available. Generate one first."},
                status=status.HTTP_404_NOT_FOUND,
            )

        from fpdf import FPDF

        pdf_doc = FPDF()
        pdf_doc.set_auto_page_break(auto=True, margin=25)
        pdf_doc.add_page()

        lines = result.rewritten_resume_text.split("\n")
        for line in lines:
            stripped = line.strip()
            if not stripped:
                pdf_doc.ln(4)
            elif stripped.isupper() and len(stripped) < 60:
                pdf_doc.ln(6)
                pdf_doc.set_font("Helvetica", "B", 13)
                pdf_doc.set_text_color(26, 26, 46)
                pdf_doc.cell(0, 7, stripped, new_x="LMARGIN", new_y="NEXT")
                # Draw underline
                pdf_doc.set_draw_color(230, 74, 25)
                pdf_doc.set_line_width(0.5)
                y = pdf_doc.get_y()
                pdf_doc.line(10, y, 200, y)
                pdf_doc.ln(3)
            elif stripped.startswith("- ") or stripped.startswith("* "):
                pdf_doc.set_font("Helvetica", "", 10)
                pdf_doc.set_text_color(34, 34, 34)
                pdf_doc.set_x(18)
                pdf_doc.multi_cell(0, 5, f"\u2022 {stripped[2:]}")
            else:
                pdf_doc.set_font("Helvetica", "", 10)
                pdf_doc.set_text_color(34, 34, 34)
                pdf_doc.multi_cell(0, 5, stripped)

        pdf = pdf_doc.output()
        jd_title = result.job_description.title or "tailored"
        filename = slugify(f"resume-{jd_title}")[:60] + ".pdf"

        response = HttpResponse(pdf, content_type="application/pdf")
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

        if not request.user.is_staff and not _deduct_credit(request.user):
            return Response(
                {"detail": "No credits remaining. Please purchase more credits."},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

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

        if not request.user.is_staff and not _deduct_credit(request.user):
            return Response(
                {"detail": "No credits remaining. Please purchase more credits."},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

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
