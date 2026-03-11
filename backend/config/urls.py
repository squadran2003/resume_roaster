from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static


def health_check(request):
    return JsonResponse({"status": "ok"})


def sentry_debug(request):
    """Raise an error to verify Sentry is capturing exceptions."""
    raise Exception("Sentry test: verify error tracking is working")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check),
    path("sentry-debug/", sentry_debug),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/resumes/", include("apps.resumes.urls")),
    path("api/v1/analysis/", include("apps.analysis.urls")),
    path("api/v1/payments/", include("apps.payments.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
