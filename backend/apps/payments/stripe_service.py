import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_upload_checkout_session(resume, success_url: str, cancel_url: str) -> str:
    """
    Create a Stripe Checkout Session for a single resume analysis.
    Price and currency are read exclusively from settings (env vars) — never hardcoded.
    Returns the hosted checkout URL.
    """
    price_cents = int(float(settings.STRIPE_UPLOAD_PRICE_USD) * 100)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": settings.STRIPE_CURRENCY,
                    "unit_amount": price_cents,
                    "product_data": {
                        "name": "Resume Analysis",
                        "description": f"AI-powered analysis: {resume.original_filename}",
                    },
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        # Store resume_id in metadata so the webhook can mark it paid
        metadata={"resume_id": str(resume.id)},
    )
    return session.url
