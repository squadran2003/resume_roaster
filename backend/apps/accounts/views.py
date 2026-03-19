import requests
from django.conf import settings
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
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


class GoogleAuthView(APIView):
    """Authenticate via Google OAuth ID token."""
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        credential = request.data.get("credential")
        
        if not credential:
            return Response(
                {"detail": "Missing credential."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        client_id = settings.GOOGLE_OAUTH_CLIENT_ID
        if not client_id:
            return Response(
                {"detail": "Google authentication is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            idinfo = google_id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                client_id,
            )
        except ValueError:
            return Response(
                {"detail": "Invalid Google token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not idinfo.get("email_verified"):
            return Response(
                {"detail": "Email not verified by Google."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = idinfo["email"].lower()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=email,
                first_name=idinfo.get("given_name", ""),
                last_name=idinfo.get("family_name", ""),
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })


class PublicConfigView(APIView):
    """Return public configuration values needed by the frontend."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "cloudflare_turnstile_site_key": settings.CLOUDFLARE_TURNSTILE_SITE_KEY,
            "google_oauth_client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        })
