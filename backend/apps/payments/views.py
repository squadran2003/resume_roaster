import logging

import stripe
from django.conf import settings
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.resumes.models import Resume

from .models import CreditPurchase
from .stripe_service import create_credit_checkout_session, create_upload_checkout_session

logger = logging.getLogger(__name__)

# Valid credit amounts from configured packs (checked at webhook fulfillment)
_VALID_CREDIT_AMOUNTS = None


def _get_valid_credit_amounts():
    global _VALID_CREDIT_AMOUNTS
    if _VALID_CREDIT_AMOUNTS is None:
        _VALID_CREDIT_AMOUNTS = {p["credits"] for p in settings.CREDIT_PACKS}
    return _VALID_CREDIT_AMOUNTS


class CreateCheckoutView(APIView):
    """Legacy per-resume checkout (kept for backwards compat)."""

    def post(self, request):
        resume_id = request.data.get("resume_id")
        if not resume_id:
            return Response(
                {"detail": "resume_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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


class CreditPacksView(APIView):
    """Return available credit packs so the frontend can display pricing."""

    def get(self, request):
        return Response({"packs": settings.CREDIT_PACKS})


class CreditCheckoutView(APIView):
    """Create a Stripe checkout session for a credit pack."""

    def post(self, request):
        pack_index = request.data.get("pack_index")
        packs = settings.CREDIT_PACKS

        if pack_index is None or not isinstance(pack_index, int) or pack_index < 0 or pack_index >= len(packs):
            return Response(
                {"detail": "Invalid pack selection."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pack = packs[pack_index]
        frontend_origin = getattr(settings, "FRONTEND_ORIGIN", "http://localhost:5173")
        success_url = f"{frontend_origin}/dashboard?payment=success"
        cancel_url = f"{frontend_origin}/dashboard?payment=cancelled"

        checkout_url = create_credit_checkout_session(
            request.user, pack, success_url, cancel_url
        )
        return Response({"checkout_url": checkout_url})


@csrf_exempt
def stripe_webhook(request):
    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET is not configured — webhook rejected")
        return HttpResponse(status=500)

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
        metadata = session.get("metadata", {})

        if metadata.get("type") == "credit_purchase":
            _handle_credit_purchase(session, metadata)
        else:
            _handle_resume_payment(session, metadata)

    return HttpResponse(status=200)


def _handle_credit_purchase(session, metadata):
    """Add credits to user's profile after successful credit pack purchase."""
    from apps.accounts.models import Profile

    user_id = metadata.get("user_id")
    credits = int(metadata.get("credits", 0))
    price_cents = int(metadata.get("price_cents", 0))
    session_id = session.get("id", "")

    if not user_id or credits <= 0:
        logger.error("Invalid credit purchase metadata: %s", metadata)
        return

    # Validate credit amount matches a known pack
    if credits not in _get_valid_credit_amounts():
        logger.error("Unexpected credit amount %d in webhook metadata", credits)
        return

    # Idempotency: skip if already processed
    if CreditPurchase.objects.filter(stripe_session_id=session_id).exists():
        logger.info("Credit purchase %s already processed, skipping", session_id)
        return

    CreditPurchase.objects.create(
        user_id=int(user_id),
        credits=credits,
        amount_cents=price_cents,
        stripe_session_id=session_id,
    )

    Profile.objects.filter(user_id=int(user_id)).update(
        credits_remaining=models.F("credits_remaining") + credits
    )
    logger.info("Added %d credits for user %s via session %s", credits, user_id, session_id)


def _handle_resume_payment(session, metadata):
    """Legacy: mark a resume as paid with ownership verification."""
    resume_id = metadata.get("resume_id")
    session_id = session.get("id", "")

    if not resume_id:
        return

    # Idempotency: use CreditPurchase table to track processed sessions
    if CreditPurchase.objects.filter(stripe_session_id=session_id).exists():
        logger.info("Resume payment session %s already processed, skipping", session_id)
        return

    try:
        # Verify the session's customer email matches the resume owner
        customer_email = session.get("customer_details", {}).get("email", "")
        resume_qs = Resume.objects.filter(id=int(resume_id))

        if customer_email:
            resume_qs = resume_qs.filter(user__email__iexact=customer_email)

        updated = resume_qs.update(is_paid=True)
        if updated:
            # Record for idempotency
            CreditPurchase.objects.create(
                user_id=resume_qs.first().user_id if resume_qs.exists() else 0,
                credits=0,
                amount_cents=int(float(settings.STRIPE_UPLOAD_PRICE_USD) * 100),
                stripe_session_id=session_id,
            )
            logger.info("Resume %s marked as paid via Stripe webhook", resume_id)
        else:
            logger.warning("Stripe webhook: resume_id %s not found or ownership mismatch", resume_id)
    except (ValueError, TypeError):
        logger.error("Stripe webhook: invalid resume_id in metadata: %s", resume_id)
