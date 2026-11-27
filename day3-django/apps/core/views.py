from .responses import success_response

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenRefreshView,
    TokenObtainPairView,
)

from .models import User, Job
from .serializers import (
    EmailTokenObtainPairSerializer,
    JobSerializer,
    PublicUserSerializer,
    SignupSerializer,
    UserSerializer,
)

from apps.recruitment.permissions import IsEmployer


# Home API
def home(request):
    return success_response(
        data={"message": "Hello the api is working"},
    )


# Signup API
class SignupAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return success_response(
            data=PublicUserSerializer(user).data,
            message="User registered successfully.",
            status_code=status.HTTP_201_CREATED
        )


# Login API
class EmailTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = EmailTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.exception:
            return response
        return success_response(
            data=response.data,
            message="Login successful.",
            status_code=response.status_code,
        )


# Refresh Token API
class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.exception:
            return response
        return success_response(
            data=response.data,
            message="Token refreshed successfully.",
            status_code=response.status_code,
        )


# Logout API
class LogoutView(TokenBlacklistView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.exception:
            return response
        return success_response(
            data={},
            message="Logout successful.",
            status_code=response.status_code,
        )


# Job List API
class JobListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)

        return success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


# Job Create API
class JobCreateAPIView(APIView):
    permission_classes = [IsEmployer]

    def post(self, request):
        serializer = JobSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )


# User Test API
class UserTestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)

        return success_response(
            data={
                "message": "User API working successfully",
                "users": serializer.data
            },
            status_code=status.HTTP_200_OK,
        )
