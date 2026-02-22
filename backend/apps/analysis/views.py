from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.resumes.models import Resume

from .models import AnalysisResult, JobDescription
from .serializers import AnalysisCreateSerializer, AnalysisResultSerializer
from .tasks import run_analysis_task
from .throttles import AIAnalysisThrottle


class AnalysisCreateView(APIView):
    throttle_classes = [AIAnalysisThrottle]

    def post(self, request):
        serializer = AnalysisCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        # Ownership enforced at query level
        resume = get_object_or_404(Resume, id=d["resume_id"], user=request.user)

        if not resume.is_paid and not request.user.is_staff:
            return Response(
                {"detail": "Payment is required before running analysis."},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        job_desc = JobDescription.objects.create(
            user=request.user,
            title=d.get("job_title", ""),
            company=d.get("company", ""),
            raw_text=d["job_description"],
        )

        result = AnalysisResult.objects.create(
            resume=resume,
            job_description=job_desc,
        )

        run_analysis_task.delay(str(result.id))

        return Response(
            AnalysisResultSerializer(result).data,
            status=status.HTTP_202_ACCEPTED,
        )


class AnalysisDetailView(APIView):
    def get(self, request, pk):
        # Ownership enforced via FK traversal — never exposes another user's data
        result = get_object_or_404(
            AnalysisResult,
            id=pk,
            resume__user=request.user,
        )
        return Response(AnalysisResultSerializer(result).data)
