from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from .models import User, Profile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password", "password_confirm")

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("subscription_tier", "credits_remaining")
        read_only_fields = ("credits_remaining",)


class MeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    payments_enabled = serializers.SerializerMethodField()
    daily_analyses_used = serializers.SerializerMethodField()
    daily_analyses_limit = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "date_joined", "is_staff", "profile", "payments_enabled", "daily_analyses_used", "daily_analyses_limit")
        read_only_fields = ("id", "email", "date_joined", "is_staff")

    def get_payments_enabled(self, obj):
        return settings.PAYMENTS_ENABLED

    def get_daily_analyses_used(self, obj):
        if settings.PAYMENTS_ENABLED:
            return None
        from apps.analysis.models import AnalysisResult, LinkedInAnalysis
        since = timezone.now() - timezone.timedelta(hours=24)
        count = AnalysisResult.objects.filter(
            resume__user=obj, created_at__gte=since
        ).count() + LinkedInAnalysis.objects.filter(
            user=obj, created_at__gte=since
        ).count()
        return count

    def get_daily_analyses_limit(self, obj):
        if settings.PAYMENTS_ENABLED:
            return None
        return settings.FREE_DAILY_ANALYSIS_LIMIT
