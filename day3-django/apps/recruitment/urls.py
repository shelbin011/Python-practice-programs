from django.urls import path
from .views import CandidateResumeUploadView, LatestJobListAPIView

from .views import (
    AdminUserListAPIView,
    AdminUserStatusAPIView,
    CandidateApplicationDetailAPIView,
    CandidateApplicationListCreateAPIView,
    EmployerApplicationListAPIView,
    EmployerJobDetailAPIView,
    EmployerJobListCreateAPIView,
    FeaturedJobListAPIView,
    PublicJobListAPIView,
    CandidateProfileCreateAPIView,
    EmployerApplicationStatusUpdateAPIView,
)

urlpatterns = [
    path("jobs/", PublicJobListAPIView.as_view(), name="public-job-list"),
    path(
        "employer/jobs/", EmployerJobListCreateAPIView.as_view(),
        name="employer-job-list-create",
    ),
    path(
        "employer/jobs/<int:pk>/", EmployerJobDetailAPIView.as_view(),
        name="employer-job-detail",
    ),
    path(
        "employer/applications/", EmployerApplicationListAPIView.as_view(),
        name="employer-application-list",
    ),
    path(
        "candidate/applications/",
        CandidateApplicationListCreateAPIView.as_view(),
        name="candidate-application-list-create",
    ),
    path(
        "candidate/applications/<int:pk>/",
        CandidateApplicationDetailAPIView.as_view(),
        name="candidate-application-detail",
    ),
    path("admin/users/", AdminUserListAPIView.as_view(), name="admin-user-list"),
    path(
        "admin/users/<int:pk>/status/",
        AdminUserStatusAPIView.as_view(),
        name="admin-user-status",
    ),
    path(
    "profiles/candidate/",
    CandidateProfileCreateAPIView.as_view(),
    name="candidate-profile-create",
    ),
    path(
        "candidate/resume/",
        CandidateResumeUploadView.as_view(),
        name="candidate-resume-upload"
    ),
    path(
    "jobs/featured/",
    FeaturedJobListAPIView.as_view(),
    name="featured-jobs"
    ),
    path(
    "jobs/latest/",
    LatestJobListAPIView.as_view(),
    name="latest-jobs"
    ),
    path(
    "employer/applications/<int:pk>/status/",
    EmployerApplicationStatusUpdateAPIView.as_view(),
    name="employer-application-status-update",
    ),
]

    