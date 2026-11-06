from django.http import JsonResponse

# Create your views here.


def home(request):
    return JsonResponse({
        "message": "Hello the api is working"
    })


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import User, Job
from .serializers import UserSerializer, JobSerializer


# 1. Job List API
class JobListAPIView(APIView):

    def get(self, request):
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# 2. Job Create API
class JobCreateAPIView(APIView):

    def post(self, request):
        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# 3. User Test API
class UserTestAPIView(APIView):

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)

        return Response({
            "message": "User API working successfully",
            "users": serializer.data
        }, status=status.HTTP_200_OK)
