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
        metadata={"resume_id": str(resume.id)},
    )
    return session.url


def create_credit_checkout_session(user, pack, success_url: str, cancel_url: str) -> str:
    """
    Create a Stripe Checkout Session for a credit pack purchase.
    Returns the hosted checkout URL.
    """
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": settings.STRIPE_CURRENCY,
                    "unit_amount": pack["price_cents"],
                    "product_data": {
                        "name": pack["label"],
                        "description": f"{pack['credits']} analysis credits",
                    },
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "type": "credit_purchase",
            "user_id": str(user.id),
            "credits": str(pack["credits"]),
            "price_cents": str(pack["price_cents"]),
        },
    )
    return session.url
