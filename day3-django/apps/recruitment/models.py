
from django.conf import settings
from django.db import models

from .validators import (
    validate_resume,
    generate_resume_filename,
)


# ==========================================
# ACTIVE PROFILE QUERYSET
# ==========================================

class ActiveProfileQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)


# ==========================================
# ACTIVE PROFILE MANAGER
# ==========================================

class ActiveProfileManager(models.Manager):

    def get_queryset(self):
        return ActiveProfileQuerySet(
            self.model,
            using=self._db
        ).active()


# ==========================================
# EMPLOYER MODEL
# ==========================================

class Employer(models.Model):

    objects = ActiveProfileManager()
    all_objects = models.Manager()

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employer_profile"
    )

    company_name = models.CharField(max_length=150)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100)

    company_size = models.CharField(
        max_length=50,
        blank=True
    )

    description = models.TextField(blank=True)

    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.company_name


# ==========================================
# CANDIDATE MODEL
# ==========================================

class Candidate(models.Model):

    objects = ActiveProfileManager()
    all_objects = models.Manager()

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="candidate_profile"
    )

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)

    skills = models.TextField(blank=True)
    education = models.TextField(blank=True)

    experience_years = models.PositiveSmallIntegerField(
        default=0
    )

    # Resume Upload
    resume = models.FileField(
        upload_to=generate_resume_filename,
        validators=[validate_resume],
        blank=True,
        null=True
    )

    expected_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Soft Delete
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def soft_delete(self):
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()

        self.save(
            update_fields=["is_deleted", "deleted_at"]
        )

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None

        self.save(
            update_fields=["is_deleted", "deleted_at"]
        )

    def __str__(self):
        return self.full_name


# ==========================================
# JOB MODEL
# ==========================================

class Job(models.Model):

    JOB_TYPE_CHOICES = [
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("internship", "Internship"),
        ("contract", "Contract"),
    ]

    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        related_name="jobs"
    )

    title = models.CharField(max_length=150)
    description = models.TextField()
    skills = models.TextField()
    experience = models.CharField(max_length=100)

    salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    salary_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    location = models.CharField(max_length=150)

    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        default="full_time"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["is_active", "-created_at"]),
            models.Index(fields=["is_active", "is_featured"]),
            models.Index(fields=["location"]),
            models.Index(fields=["job_type"]),
        ]

    def __str__(self):
        return self.title


# ==========================================
# APPLICATION MODEL
# ==========================================

class Application(models.Model):

    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("screening", "Screening"),
        ("shortlisted", "Shortlisted"),
        ("interview_scheduled", "Interview Scheduled"),
        ("rejected", "Rejected"),
        ("hired", "Hired"),
        ("selected", "Selected"),
    ]

    ALLOWED_TRANSITIONS = {
        "applied": ["shortlisted", "rejected"],
        "screening": ["shortlisted", "rejected"],
        "shortlisted": ["interview_scheduled", "rejected"],
        "interview_scheduled": ["selected", "rejected"],
        "selected": [],
        "rejected": [],
        "hired": [],
    }

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    resume_snapshot = models.FileField(
        upload_to="application_resumes/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="applied"
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["candidate", "job"],
                name="unique_candidate_job_application"
            )
        ]

    def can_transition_to(self, new_status):
        return new_status in self.ALLOWED_TRANSITIONS.get(
            self.status, []
        )

    def __str__(self):
        return f"{self.candidate} - {self.job}"

class ApplicationStatusHistory(models.Model):

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="status_history"
    )

    old_status = models.CharField(
        max_length=30
    )

    new_status = models.CharField(
        max_length=30,
        choices=Application.STATUS_CHOICES
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="application_status_changes"
    )

    changed_at = models.DateTimeField(auto_now_add=True)

    remarks = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return (
            f"Application {self.application_id}: "
            f"{self.old_status} -> {self.new_status}"
        )
