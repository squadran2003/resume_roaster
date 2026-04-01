import secrets
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
        null=True, blank=True, help_text="0-100"
    )
    ats_flags = models.JSONField(default=list, blank=True)
    rewritten_bullets = models.JSONField(default=list, blank=True)
    hire_probability = models.FloatField(null=True, blank=True, help_text="0.0-1.0")
    cover_letter = models.TextField(blank=True)

    # V2 fields
    keyword_matches = models.JSONField(
        default=list, blank=True,
        help_text='[{"keyword": str, "found": bool, "section_hint": str}]',
    )
    follow_up_emails = models.JSONField(
        default=list, blank=True,
        help_text='[{"type": str, "subject": str, "body": str}]',
    )
    rewritten_resume_text = models.TextField(
        blank=True,
        help_text="Full AI-rewritten resume content tailored to the JD",
    )
    rewritten_resume_json = models.JSONField(
        null=True, blank=True,
        help_text='Structured rewrite: {"name", "contact", "summary", "sections": [...]}',
    )
    interview_questions = models.JSONField(
        default=list, blank=True,
        help_text='[{"question": str, "why_asked": str, "answer_framework": str}]',
    )

    share_token = models.CharField(
        max_length=32, unique=True, blank=True, null=True,
        help_text="Public token for sharing score card",
    )

    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Analysis {self.id} [{self.status}]"


class LinkedInAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="linkedin_analyses",
    )
    job_description = models.ForeignKey(
        JobDescription, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="linkedin_analyses",
    )
    headline = models.CharField(max_length=500)
    about = models.TextField()
    jd_text = models.TextField()

    # AI results
    headline_rewrite = models.CharField(max_length=500, blank=True)
    about_rewrite = models.TextField(blank=True)
    suggested_skills = models.JSONField(default=list, blank=True)
    recruiter_keywords = models.JSONField(default=list, blank=True)
    score = models.PositiveSmallIntegerField(null=True, blank=True)
    tips = models.JSONField(default=list, blank=True)

    status = models.CharField(
        max_length=20,
        choices=AnalysisResult.Status.choices,
        default=AnalysisResult.Status.PENDING,
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"LinkedIn Analysis {self.id} [{self.status}]"
