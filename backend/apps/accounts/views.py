import requests
from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import RegisterSerializer, MeSerializer


def verify_turnstile(token, remote_ip=None):
    """Verify a Cloudflare Turnstile token. Returns True if valid or if Turnstile is not configured."""
    secret = settings.CLOUDFLARE_TURNSTILE_SECRET_KEY
    if not secret:
        return True  # Turnstile not configured, skip verification

    if not token:
        return False

    payload = {"secret": secret, "response": token}

    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        resp = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data=payload,
            timeout=10,
        )
        return resp.json().get("success", False)
    except (requests.RequestException, ValueError):
        return False


class TurnstileTokenObtainPairView(TokenObtainPairView):
    """JWT token endpoint with Cloudflare Turnstile verification."""

    def post(self, request, *args, **kwargs):
        turnstile_token = request.data.get("turnstile_token")
        remote_ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR")

        if not verify_turnstile(turnstile_token, remote_ip):
            return Response(
                {"detail": "Bot verification failed. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().post(request, *args, **kwargs)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        turnstile_token = request.data.get("turnstile_token")
        remote_ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR")

        if not verify_turnstile(turnstile_token, remote_ip):
            return Response(
                {"detail": "Bot verification failed. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "Account created successfully.", "email": user.email},
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = MeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PublicConfigView(APIView):
    """Return public configuration values needed by the frontend."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "cloudflare_turnstile_site_key": settings.CLOUDFLARE_TURNSTILE_SITE_KEY,
        })
