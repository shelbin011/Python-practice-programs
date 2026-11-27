
import os
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


MAX_RESUME_SIZE = 5 * 1024 * 1024

resume_extension_validator = FileExtensionValidator(
    allowed_extensions=["pdf", "doc", "docx"]
)


def validate_resume(file):

    resume_extension_validator(file)

    if file.size > MAX_RESUME_SIZE:
        raise ValidationError(
            "Resume size cannot exceed 5 MB."
        )

    if file.size == 0:
        raise ValidationError(
            "Empty files are not allowed."
        )


def generate_resume_filename(instance, filename):

    extension = os.path.splitext(filename)[1].lower()

    unique_filename = f"{uuid.uuid4().hex}{extension}"

    return f"resumes/candidates/{unique_filename}"
