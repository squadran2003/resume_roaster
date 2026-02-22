import logging

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.resumes.models import Resume

from .stripe_service import create_upload_checkout_session

logger = logging.getLogger(__name__)


class CreateCheckoutView(APIView):
    def post(self, request):
        resume_id = request.data.get("resume_id")
        if not resume_id:
            return Response(
                {"detail": "resume_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ownership enforced at query level
        resume = get_object_or_404(Resume, id=resume_id, user=request.user)

        if resume.is_paid:
            return Response(
                {"detail": "This resume has already been paid for."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        frontend_origin = getattr(settings, "FRONTEND_ORIGIN", "http://localhost:5173")
        success_url = f"{frontend_origin}/dashboard?payment=success"
        cancel_url = f"{frontend_origin}/dashboard?payment=cancelled"

        checkout_url = create_upload_checkout_session(resume, success_url, cancel_url)
        return Response({"checkout_url": checkout_url})


@csrf_exempt
def stripe_webhook(request):
    """
    Stripe sends events here. Signature verified before any processing.
    Only checkout.session.completed marks a resume as paid.
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.warning("Stripe webhook received invalid payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.warning("Stripe webhook signature verification failed")
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        resume_id = session.get("metadata", {}).get("resume_id")
        if resume_id:
            try:
                updated = Resume.objects.filter(id=int(resume_id)).update(is_paid=True)
                if updated:
                    logger.info("Resume %s marked as paid via Stripe webhook", resume_id)
                else:
                    logger.warning("Stripe webhook: resume_id %s not found", resume_id)
            except (ValueError, TypeError):
                logger.error("Stripe webhook: invalid resume_id in metadata: %s", resume_id)

    return HttpResponse(status=200)
