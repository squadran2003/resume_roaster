import uuid

from django.conf import settings
from django.db import models

from apps.resumes.models import Resume


class JobDescription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_descriptions",
    )
    title = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    raw_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} @ {self.company}" if self.title else f"JD #{self.id}"


class AnalysisResult(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        DONE = "done", "Done"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="analyses")
    job_description = models.ForeignKey(
        JobDescription, on_delete=models.CASCADE, related_name="analyses"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    match_score = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="0–100"
    )
    ats_flags = models.JSONField(default=list, blank=True)
    rewritten_bullets = models.JSONField(default=list, blank=True)
    hire_probability = models.FloatField(null=True, blank=True, help_text="0.0–1.0")
    cover_letter = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Analysis {self.id} [{self.status}]"
