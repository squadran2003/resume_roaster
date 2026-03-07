from rest_framework import serializers

from .models import AnalysisResult, LinkedInAnalysis


class AnalysisCreateSerializer(serializers.Serializer):
    resume_id = serializers.IntegerField()
    job_description = serializers.CharField(min_length=100, max_length=20000)
    job_title = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    company = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")


class AnalysisResultSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job_description.title", read_only=True)
    company = serializers.CharField(source="job_description.company", read_only=True)
    resume_filename = serializers.CharField(source="resume.original_filename", read_only=True)

    class Meta:
        model = AnalysisResult
        fields = [
            "id",
            "status",
            "match_score",
            "hire_probability",
            "ats_flags",
            "rewritten_bullets",
            "cover_letter",
            "keyword_matches",
            "follow_up_emails",
            "interview_questions",
            "rewritten_resume_text",
            "job_title",
            "company",
            "resume_filename",
            "created_at",
            "completed_at",
        ]
        read_only_fields = fields


class LinkedInCreateSerializer(serializers.Serializer):
    headline = serializers.CharField(max_length=500)
    about = serializers.CharField(min_length=50, max_length=5000)
    jd_text = serializers.CharField(min_length=100, max_length=20000)


class LinkedInAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkedInAnalysis
        fields = [
            "id",
            "status",
            "headline",
            "about",
            "headline_rewrite",
            "about_rewrite",
            "suggested_skills",
            "recruiter_keywords",
            "score",
            "tips",
            "created_at",
        ]
        read_only_fields = fields
