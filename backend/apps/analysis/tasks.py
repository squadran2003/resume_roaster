import logging

import sentry_sdk
from celery import shared_task
from django.utils import timezone

from .ai_service import run_analysis, run_interview_prep, run_linkedin_analysis, run_resume_rewrite
from .models import AnalysisResult, LinkedInAnalysis

logger = logging.getLogger(__name__)


def _safe_error_message(exc: Exception) -> str:
    """Return a user-safe error message — never expose raw exception details."""
    exc_type = type(exc).__name__.lower()
    exc_str = str(exc).lower()
    if "api" in exc_str or "key" in exc_str or "auth" in exc_str:
        return "AI service temporarily unavailable. Please try again."
    if "json" in exc_str or "valueerror" in exc_type:
        return "AI returned an unexpected response. Please try again."
    return "Analysis failed. Please try again later."


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def run_analysis_task(self, analysis_id: str):
    try:
        result = AnalysisResult.objects.select_related(
            "resume", "job_description"
        ).get(id=analysis_id)
    except AnalysisResult.DoesNotExist:
        logger.error("AnalysisResult %s not found — task aborted", analysis_id)
        return

    result.status = AnalysisResult.Status.PROCESSING
    result.save(update_fields=["status"])

    try:
        data = run_analysis(
            result.resume.parsed_text,
            result.job_description.raw_text,
        )
        result.match_score = max(0, min(100, int(data.get("match_score", 0))))
        result.hire_probability = max(0.0, min(1.0, float(data.get("hire_probability", 0.0))))
        result.ats_flags = data.get("ats_flags", [])
        result.rewritten_bullets = data.get("rewritten_bullets", [])
        result.cover_letter = data.get("cover_letter", "")
        result.keyword_matches = data.get("keyword_matches", [])
        result.follow_up_emails = data.get("follow_up_emails", [])
        result.status = AnalysisResult.Status.DONE
        result.completed_at = timezone.now()
        result.save()
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        logger.exception("Analysis task failed for %s", analysis_id)
        result.status = AnalysisResult.Status.FAILED
        result.error_message = _safe_error_message(exc)
        result.save(update_fields=["status", "error_message"])


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def run_resume_rewrite_task(self, analysis_id: str):
    """Generate a full resume rewrite for an existing analysis (costs 1 credit, deducted before dispatch)."""
    try:
        result = AnalysisResult.objects.select_related(
            "resume", "job_description"
        ).get(id=analysis_id)
    except AnalysisResult.DoesNotExist:
        logger.error("AnalysisResult %s not found for rewrite — task aborted", analysis_id)
        return

    try:
        rewritten = run_resume_rewrite(
            result.resume.parsed_text,
            result.job_description.raw_text,
        )
        result.rewritten_resume_text = rewritten
        result.save(update_fields=["rewritten_resume_text"])
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        logger.exception("Resume rewrite task failed for %s", analysis_id)


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def run_interview_prep_task(self, analysis_id: str):
    """Generate interview prep questions (costs 1 credit, deducted before dispatch)."""
    try:
        result = AnalysisResult.objects.select_related(
            "resume", "job_description"
        ).get(id=analysis_id)
    except AnalysisResult.DoesNotExist:
        logger.error("AnalysisResult %s not found for interview prep — task aborted", analysis_id)
        return

    try:
        questions = run_interview_prep(
            result.resume.parsed_text,
            result.job_description.raw_text,
        )
        result.interview_questions = questions
        result.save(update_fields=["interview_questions"])
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        logger.exception("Interview prep task failed for %s", analysis_id)
        result.error_message = _safe_error_message(exc)
        result.save(update_fields=["error_message"])


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def run_linkedin_task(self, linkedin_id: str):
    """Run LinkedIn optimization analysis (costs 1 credit, deducted before dispatch)."""
    try:
        obj = LinkedInAnalysis.objects.get(id=linkedin_id)
    except LinkedInAnalysis.DoesNotExist:
        logger.error("LinkedInAnalysis %s not found — task aborted", linkedin_id)
        return

    obj.status = "processing"
    obj.save(update_fields=["status"])

    try:
        data = run_linkedin_analysis(obj.headline, obj.about, obj.jd_text)
        obj.headline_rewrite = data.get("headline_rewrite", "")
        obj.about_rewrite = data.get("about_rewrite", "")
        obj.suggested_skills = data.get("suggested_skills", [])
        obj.recruiter_keywords = data.get("recruiter_keywords", [])
        obj.score = max(0, min(100, int(data.get("score", 0))))
        obj.tips = data.get("tips", [])
        obj.status = "done"
        obj.save()
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        logger.exception("LinkedIn analysis task failed for %s", linkedin_id)
        obj.status = "failed"
        obj.error_message = _safe_error_message(exc)
        obj.save(update_fields=["status", "error_message"])
