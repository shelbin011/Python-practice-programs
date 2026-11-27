from django.urls import path
from . import views
from .views import (
    EmailTokenObtainPairView,
    JobListAPIView,
    JobCreateAPIView,
    LogoutView,
    RefreshTokenView,
    SignupAPIView,
    UserTestAPIView
)

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/signup/', SignupAPIView.as_view(), name='auth-signup'),
    path('auth/login/', EmailTokenObtainPairView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='auth-refresh'),
    path('jobs/', JobListAPIView.as_view(), name='job-list'),
    path('jobs/create/', JobCreateAPIView.as_view(), name='job-create'),
    path('users/test/', UserTestAPIView.as_view(), name='user-test'),
]
