from rest_framework import serializers

from .models import AnalysisResult


class AnalysisCreateSerializer(serializers.Serializer):
    resume_id = serializers.IntegerField()
    job_description = serializers.CharField(min_length=100)
    job_title = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    company = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")


class AnalysisResultSerializer(serializers.ModelSerializer):
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
            "created_at",
            "completed_at",
        ]
        read_only_fields = fields
