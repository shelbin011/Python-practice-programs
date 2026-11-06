from django.contrib import admin
from .models import Employer, Candidate, Job, Application
# Register your models here.



@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ("id", "company_name", "industry", "created_at")
    search_fields = ("company_name", "industry")


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        "id", "full_name", "phone", "experience_years"
    )
    search_fields = ("full_name", "phone")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "employer", "location", "is_active"
    )
    list_filter = ("is_active", "location")
    search_fields = ("title", "employer__company_name")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "candidate", "job", "status", "applied_at"
    )
    list_filter = ("status", "applied_at")
    search_fields = (
        "candidate__full_name", "job__title"
    )
