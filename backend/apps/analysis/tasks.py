import logging

from celery import shared_task
from django.utils import timezone

from .ai_service import run_analysis
from .models import AnalysisResult

logger = logging.getLogger(__name__)


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
        result.status = AnalysisResult.Status.DONE
        result.completed_at = timezone.now()
        result.save()
    except Exception as exc:
        logger.exception("Analysis task failed for %s", analysis_id)
        result.status = AnalysisResult.Status.FAILED
        result.error_message = str(exc)
        result.save(update_fields=["status", "error_message"])