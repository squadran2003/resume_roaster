from django.core.files.storage import default_storage
from rest_framework import serializers

from .models import Resume
from .validators import validate_resume_file
from .parsers import extract_text


class ResumeSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField(read_only=True)
    file = serializers.FileField(write_only=True)

    class Meta:
        model = Resume
        fields = [
            "id",
            "original_filename",
            "file_size",
            "mime_type",
            "uploaded_at",
            "is_paid",
            "download_url",
            "file",
        ]
        read_only_fields = [
            "id",
            "original_filename",
            "file_size",
            "mime_type",
            "uploaded_at",
            "is_paid",
            "download_url",
        ]

    def validate_file(self, value):
        # MIME validation via magic bytes
        mime_type = validate_resume_file(value)
        # Stash for use in create()
        self._detected_mime = mime_type
        return value

    def create(self, validated_data):
        file = validated_data["file"]
        mime_type = getattr(self, "_detected_mime", "")
        parsed_text = extract_text(file, mime_type)
        file.seek(0)

        resume = Resume.objects.create(
            user=self.context["request"].user,
            file=file,
            original_filename=file.name,
            file_size=file.size,
            mime_type=mime_type,
            parsed_text=parsed_text,
        )
        return resume

    def get_download_url(self, obj):
        """
        Generate a presigned URL (S3) or a media URL (local dev).
        Never exposes raw storage path or bucket name.
        """
        if not obj.file:
            return None
        return default_storage.url(obj.file.name)
