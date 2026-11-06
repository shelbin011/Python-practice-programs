from django.urls import path
from . import views
from .views import (
    JobListAPIView,
    JobCreateAPIView,
    UserTestAPIView
)

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/', JobListAPIView.as_view(), name='job-list'),
    path('jobs/create/', JobCreateAPIView.as_view(), name='job-create'),
    path('users/test/', UserTestAPIView.as_view(), name='user-test'),
]
