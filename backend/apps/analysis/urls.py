from django.urls import path

from .views import (
    AnalysisCompareView,
    AnalysisCreateView,
    AnalysisDetailView,
    AnalysisListView,
    InterviewPrepView,
    LinkedInAnalyzeView,
    LinkedInDetailView,
    ResumeRewritePDFView,
    ResumeRewriteView,
)

urlpatterns = [
    path("", AnalysisCreateView.as_view(), name="analysis-create"),
    path("list/", AnalysisListView.as_view(), name="analysis-list"),
    path("compare/", AnalysisCompareView.as_view(), name="analysis-compare"),
    path("<uuid:pk>/", AnalysisDetailView.as_view(), name="analysis-detail"),
    path("<uuid:pk>/rewrite/", ResumeRewriteView.as_view(), name="analysis-rewrite"),
    path("<uuid:pk>/rewrite/pdf/", ResumeRewritePDFView.as_view(), name="analysis-rewrite-pdf"),
    path("<uuid:pk>/interview-prep/", InterviewPrepView.as_view(), name="analysis-interview-prep"),
    path("linkedin/", LinkedInAnalyzeView.as_view(), name="linkedin-analyze"),
    path("linkedin/<uuid:pk>/", LinkedInDetailView.as_view(), name="linkedin-detail"),
]
