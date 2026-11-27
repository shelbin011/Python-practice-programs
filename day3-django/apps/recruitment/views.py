
# Django imports
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

# Third-party imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.views import APIView

# Project imports
from apps.core.responses import (
    SuccessResponseMixin,
    success_response,
)

# Recruitment models
from .models import (
    Application,
    ApplicationStatusHistory,
    Candidate,
    Job,
)

# Recruitment permissions
from .permissions import (
    IsAdmin,
    IsCandidate,
    IsCandidateOwner,
    IsEmployer,
    IsEmployerOwner,
)

# Recruitment serializers
from .serializers import (
    AccountStatusSerializer,
    AdminUserSerializer,
    ApplicationSerializer,
    ApplicationStatusUpdateSerializer,
    CandidateApplicationCreateSerializer,
    CandidateProfileSerializer,
    RecruitmentJobSerializer,
    ResumeUploadSerializer,
)

from .filters import JobFilter


# Helper functions
def current_employer(user):
    try:
        return user.employer_profile
    except ObjectDoesNotExist as exc:
        raise PermissionDenied(
            "An employer profile is required."
        ) from exc


def current_candidate(user):
    try:
        return user.candidate_profile
    except ObjectDoesNotExist as exc:
        raise PermissionDenied(
            "A candidate profile is required."
        ) from exc


# Day 17 - Public Job Listing, Filtering and Search
class PublicJobListAPIView(
    SuccessResponseMixin,
    generics.ListAPIView,
):
    permission_classes = [AllowAny]
    serializer_class = RecruitmentJobSerializer

    filterset_class = JobFilter
    filter_backends = [DjangoFilterBackend, SearchFilter]

    search_fields = [
        "title",
        "description",
        "location",
        "skills",
    ]

    def get_queryset(self):
        return Job.objects.filter(
            is_active=True
        ).select_related(
            "employer"
        ).order_by("-created_at", "-id")


class FeaturedJobListAPIView(
    SuccessResponseMixin,
    generics.ListAPIView,
):
    permission_classes = [AllowAny]
    serializer_class = RecruitmentJobSerializer

    def get_queryset(self):
        return Job.objects.filter(
            is_active=True,
            is_featured=True,
        ).select_related(
            "employer"
        ).order_by("-created_at")


class LatestJobListAPIView(
    SuccessResponseMixin,
    generics.ListAPIView,
):
    permission_classes = [AllowAny]
    serializer_class = RecruitmentJobSerializer

    def get_queryset(self):
        return Job.objects.filter(
            is_active=True
        ).select_related(
            "employer"
        ).order_by("-created_at")


# Day 16 - Employer Job Management
class EmployerJobListCreateAPIView(
    SuccessResponseMixin,
    generics.ListCreateAPIView,
):
    permission_classes = [IsEmployer]
    serializer_class = RecruitmentJobSerializer

    def get_queryset(self):
        return Job.objects.filter(
            employer__user=self.request.user
        ).select_related("employer")

    def perform_create(self, serializer):
        serializer.save(
            employer=current_employer(self.request.user)
        )


class EmployerJobDetailAPIView(
    SuccessResponseMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    permission_classes = [IsEmployerOwner]
    serializer_class = RecruitmentJobSerializer

    def get_queryset(self):
        return Job.objects.filter(
            employer__user=self.request.user
        ).select_related("employer")


# Day 18 - Employer Application Tracking
class EmployerApplicationListAPIView(
    SuccessResponseMixin,
    generics.ListAPIView,
):
    permission_classes = [IsEmployer]
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        return Application.objects.filter(
            job__employer__user=self.request.user
        ).select_related("candidate", "job")


# Day 19 - Employer Application Status Update
class EmployerApplicationStatusUpdateAPIView(
    SuccessResponseMixin,
    generics.UpdateAPIView,
):
    permission_classes = [IsEmployer]
    serializer_class = ApplicationStatusUpdateSerializer
    http_method_names = ["patch", "head", "options"]

    def get_queryset(self):
        return Application.objects.filter(
            job__employer__user=self.request.user
        )

    @transaction.atomic
    def perform_update(self, serializer):
        application = serializer.instance
        old_status = application.status

        updated_application = serializer.save()

        ApplicationStatusHistory.objects.create(
            application=updated_application,
            old_status=old_status,
            new_status=updated_application.status,
            changed_by=self.request.user,
            remarks=serializer.validated_data.get("remarks", ""),
        )


# Day 18 - Candidate Application Management
class CandidateApplicationListCreateAPIView(
    SuccessResponseMixin,
    generics.ListCreateAPIView,
):
    permission_classes = [IsCandidateOwner]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CandidateApplicationCreateSerializer
        return ApplicationSerializer

    def get_queryset(self):
        return Application.objects.filter(
            candidate__user=self.request.user
        ).select_related("candidate", "job")

    def perform_create(self, serializer):
        candidate = current_candidate(self.request.user)

        if Application.objects.filter(
            candidate=candidate,
            job=serializer.validated_data["job"],
        ).exists():
            raise ValidationError(
                {"job_id": "You have already applied for this job."}
            )

        serializer.save(candidate=candidate)


class CandidateApplicationDetailAPIView(
    SuccessResponseMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    permission_classes = [IsCandidateOwner]
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        return Application.objects.filter(
            candidate__user=self.request.user
        ).select_related("candidate", "job")


# Admin User Management
class AdminUserListAPIView(
    SuccessResponseMixin,
    generics.ListAPIView,
):
    permission_classes = [IsAdmin]
    serializer_class = AdminUserSerializer
    queryset = User.objects.prefetch_related("groups").all()


class AdminUserStatusAPIView(
    SuccessResponseMixin,
    generics.UpdateAPIView,
):
    permission_classes = [IsAdmin]
    serializer_class = AccountStatusSerializer
    queryset = User.objects.all()
    http_method_names = ["patch", "head", "options"]

    def perform_update(self, serializer):
        if (
            self.get_object() == self.request.user
            and serializer.validated_data.get("is_active") is False
        ):
            raise PermissionDenied(
                "You cannot deactivate your own account."
            )

        serializer.save()


# Candidate Profile Management
class CandidateProfileCreateAPIView(
    SuccessResponseMixin,
    generics.CreateAPIView,
):
    permission_classes = [IsCandidate]
    serializer_class = CandidateProfileSerializer

    def perform_create(self, serializer):
        # Prevent duplicate profiles, including deleted ones
        if Candidate.all_objects.filter(
            user=self.request.user
        ).exists():
            raise ValidationError(
                "You already have a candidate profile."
            )

        # Automatically assign the authenticated user
        serializer.save(user=self.request.user)


# Day 12 - Candidate Resume Upload
class CandidateResumeUploadView(APIView):
    permission_classes = [IsAuthenticated, IsCandidate]

    def get_candidate(self, request):
        try:
            return Candidate.objects.get(user=request.user)
        except Candidate.DoesNotExist:
            raise NotFound("Candidate profile not found.")

    def get(self, request):
        candidate = self.get_candidate(request)

        if not candidate.resume:
            raise NotFound("No resume uploaded yet.")

        return success_response(
            data={
                "message": "Resume retrieved successfully.",
                "resume": request.build_absolute_uri(
                    candidate.resume.url
                ),
            },
            status_code=status.HTTP_200_OK,
        )

    def post(self, request):
        candidate = self.get_candidate(request)

        if candidate.resume:
            raise ValidationError(
                "A resume already exists. Use PUT to replace it."
            )

        serializer = ResumeUploadSerializer(
            candidate,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(
            data={
                "message": "Resume uploaded successfully.",
                "resume": request.build_absolute_uri(
                    candidate.resume.url
                ),
            },
            status_code=status.HTTP_200_OK,
        )

    def put(self, request):
        candidate = self.get_candidate(request)

        old_resume = (
            candidate.resume.name if candidate.resume else None
        )
        old_storage = (
            candidate.resume.storage if candidate.resume else None
        )

        serializer = ResumeUploadSerializer(
            candidate,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if old_resume and old_resume != candidate.resume.name:
            old_storage.delete(old_resume)

        return success_response(
            data={
                "message": "Resume replaced successfully.",
                "resume": request.build_absolute_uri(
                    candidate.resume.url
                ),
            },
            status_code=status.HTTP_200_OK,
        )

    def delete(self, request):
        candidate = self.get_candidate(request)

        if not candidate.resume:
            raise NotFound("No resume available to delete.")

        storage = candidate.resume.storage
        old_resume = candidate.resume.name

        candidate.resume = None
        candidate.save(update_fields=["resume"])

        storage.delete(old_resume)

        return success_response(
            data={"message": "Resume deleted successfully."},
            status_code=status.HTTP_200_OK,
        )
