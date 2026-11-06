
from django.conf import settings
from django.db import models


class Employer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employer_profile"
    )
    company_name = models.CharField(max_length=150)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name


class Candidate(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="candidate_profile"
    )
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    skills = models.TextField(blank=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    resume = models.FileField(
        upload_to="resumes/",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class Job(models.Model):
    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        related_name="jobs"
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    location = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Application(models.Model):
    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("screening", "Screening"),
        ("shortlisted", "Shortlisted"),
        ("rejected", "Rejected"),
        ("hired", "Hired"),
    ]

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

    def __str__(self):
        return f"{self.candidate} - {self.job}"
