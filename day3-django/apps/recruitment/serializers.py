from pathlib import Path
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.files.base import ContentFile

from rest_framework import serializers

from .models import (
    Application,
    Candidate,
    Employer,
    Job,
)

class RecruitmentJobSerializer(serializers.ModelSerializer):
    employer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Job
        fields = (
            "id",
            "employer",
            "title",
            "description",
            "skills",
            "experience",
            "salary_min",
            "salary_max",
            "location",
            "job_type",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "employer",
            "created_at",
            "updated_at",
        )


class ApplicationSerializer(serializers.ModelSerializer):
    candidate = serializers.PrimaryKeyRelatedField(read_only=True)
    job = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Application
        fields = (
            "id",
            "candidate",
            "job",
            "status",
            "applied_at",
            "resume_snapshot",
        )
        read_only_fields = (
            "id",
            "candidate",
            "job",
            "applied_at",
            "resume_snapshot",
        )


class CandidateApplicationCreateSerializer(ApplicationSerializer):

    job_id = serializers.PrimaryKeyRelatedField(
        source="job",
        queryset=Job.objects.filter(is_active=True),
        write_only=True,
    )

    class Meta(ApplicationSerializer.Meta):
        fields = (
            "id",
            "candidate",
            "job",
            "job_id",
            "status",
            "applied_at",
            "resume_snapshot",
        )
        read_only_fields = (
            "id",
            "candidate",
            "job",
            "applied_at",
            "resume_snapshot",
        )

    def create(self, validated_data):
        candidate = validated_data["candidate"]

        # Create the application record first
        application = super().create(validated_data)

        # Copy the candidate's current resume, if available
        if candidate.resume:
            resume_name = candidate.resume.name
            extension = Path(resume_name).suffix

            candidate.resume.open("rb")
            try:
                resume_content = candidate.resume.read()
            finally:
                candidate.resume.close()

            snapshot_name = (
                f"application_{application.id}_{uuid4().hex}{extension}"
            )

            application.resume_snapshot.save(
                snapshot_name,
                ContentFile(resume_content),
                save=True
            )

        return application


class AdminUserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name",
            "is_active", "is_staff", "groups",
        )
        read_only_fields = fields


class AccountStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("is_active",)

    def to_internal_value(self, data):
        forbidden_fields = {
            "groups", "is_staff", "is_superuser", "role", "username", "email"
        }
        submitted_forbidden_fields = forbidden_fields.intersection(data)
        if submitted_forbidden_fields:
            raise serializers.ValidationError(
                {
                    field: "Role and identity fields cannot be changed through this API."
                    for field in sorted(submitted_forbidden_fields)
                }
            )
        return super().to_internal_value(data)



class CandidateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate

        fields = [
            "id",
            "full_name",
            "phone",
            "skills",
            "education",
            "experience_years",
            "expected_salary",
            "resume",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_phone(self, value):
        import re

        if not re.fullmatch(r"^\+?[0-9]{7,15}$", value):
            raise serializers.ValidationError(
                "Enter a valid phone number."
            )

        return value

    def validate_expected_salary(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Expected salary cannot be negative."
            )

        return value

    def validate_experience_years(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Experience cannot be negative."
            )

        return value


class EmployerProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employer

        fields = [
            "id",
            "company_name",
            "website",
            "industry",
            "company_size",
            "description",
            "is_verified",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "is_verified",
            "created_at",
            "updated_at",
        ]

    def validate_company_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Company name must contain at least 2 characters."
            )

        return value.strip()

    def validate_industry(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Industry cannot be empty."
            )

        return value.strip()

    def validate_website(self, value):
        if value and not value.startswith(("http://", "https://")):
            raise serializers.ValidationError(
                "Website must start with http:// or https://."
            )

        return value



#day 12 implementation


from rest_framework import serializers
from .models import Candidate


class ResumeUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        fields = ["resume"]

    def validate_resume(self, value):

        if not value:
            raise serializers.ValidationError(
                "Please upload a resume."
            )

        # Additional size validation
        max_size = 5 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(
                "Resume cannot exceed 5 MB."
            )

        return value


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):

    remarks = serializers.CharField(
        required=False,
        allow_blank=True
    )

    class Meta:
        model = Application
        fields = ("status", "remarks")

    def validate_status(self, value):
        if not self.instance.can_transition_to(value):
            raise serializers.ValidationError(
                f"Cannot change status from "
                f"'{self.instance.status}' to '{value}'."
            )

        return value