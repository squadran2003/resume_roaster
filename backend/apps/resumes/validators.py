import magic
from django.core.exceptions import ValidationError

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def validate_resume_file(file):
    """
    Validate upload by reading magic bytes (not trusting extension).
    Raises ValidationError on failure.
    """
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(
            f"File too large. Maximum allowed size is 5 MB; received {file.size} bytes."
        )

    # Read first 2 KB for MIME detection
    header = file.read(2048)
    file.seek(0)

    detected_mime = magic.from_buffer(header, mime=True)
    if detected_mime not in ALLOWED_MIME_TYPES:
        raise ValidationError(
            f"Unsupported file type '{detected_mime}'. Only PDF and DOCX files are accepted."
        )

    return detected_mime
