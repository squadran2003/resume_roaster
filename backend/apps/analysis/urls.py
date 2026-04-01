from django.urls import path

from .views import (
    AnalysisCompareView,
    AnalysisCreateView,
    AnalysisDetailView,
    AnalysisListView,
    InterviewPrepView,
    LinkedInAnalyzeView,
    LinkedInDetailView,
    PublicShareView,
    ResumeRewriteDOCXView,
    ResumeRewritePDFView,
    ResumeRewriteView,
    ScoreCardImageView,
    ShareTokenView,
)

urlpatterns = [
    path("", AnalysisCreateView.as_view(), name="analysis-create"),
    path("list/", AnalysisListView.as_view(), name="analysis-list"),
    path("compare/", AnalysisCompareView.as_view(), name="analysis-compare"),
    path("<uuid:pk>/", AnalysisDetailView.as_view(), name="analysis-detail"),
    path("<uuid:pk>/rewrite/", ResumeRewriteView.as_view(), name="analysis-rewrite"),
    path("<uuid:pk>/rewrite/pdf/", ResumeRewritePDFView.as_view(), name="analysis-rewrite-pdf"),
    path("<uuid:pk>/rewrite/docx/", ResumeRewriteDOCXView.as_view(), name="analysis-rewrite-docx"),
    path("<uuid:pk>/interview-prep/", InterviewPrepView.as_view(), name="analysis-interview-prep"),
    path("<uuid:pk>/share/", ShareTokenView.as_view(), name="analysis-share"),
    path("shared/<str:token>/", PublicShareView.as_view(), name="analysis-public-share"),
    path("shared/<str:token>/image.png", ScoreCardImageView.as_view(), name="analysis-share-image"),
    path("linkedin/", LinkedInAnalyzeView.as_view(), name="linkedin-analyze"),
    path("linkedin/<uuid:pk>/", LinkedInDetailView.as_view(), name="linkedin-detail"),
]
