from django.contrib.auth.models import Group, User as AuthUser
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ("id", "email", "first_name", "last_name")


class SignupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    def validate_email(self, value):
        normalized_email = value.strip().lower()
        if AuthUser.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return normalized_email

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = AuthUser.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=validated_data["name"].strip(),
            password=validated_data["password"],
        )
        candidate_group, _ = Group.objects.get_or_create(name="Candidate")
        user.groups.add(candidate_group)
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        password = attrs["password"]
        user = AuthUser.objects.filter(email__iexact=email).first()

        if user is None or not user.is_active or not user.check_password(password):
            from rest_framework.exceptions import AuthenticationFailed

            raise AuthenticationFailed(
                "No active account found with the given credentials."
            )

        self.user = user
        refresh = self.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": PublicUserSerializer(user).data,
        }
