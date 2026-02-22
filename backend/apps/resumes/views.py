from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Resume
from .serializers import ResumeSerializer


class ResumeListCreateView(generics.ListCreateAPIView):
    serializer_class = ResumeSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # Always scoped to the authenticated user — no cross-user access
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


class ResumeDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ResumeSerializer

    def get_object(self):
        # Ownership enforced at query level, not just permission check
        return get_object_or_404(Resume, id=self.kwargs["pk"], user=self.request.user)

    def perform_destroy(self, instance):
        # Remove the physical file from storage before deleting the DB row
        instance.file.delete(save=False)
        instance.delete()
