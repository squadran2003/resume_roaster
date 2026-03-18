from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, MeView, TurnstileTokenObtainPairView, PublicConfigView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("token/", TurnstileTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("config/", PublicConfigView.as_view(), name="public-config"),
]
