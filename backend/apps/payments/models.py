from django.conf import settings
from django.db import models


class CreditPurchase(models.Model):
    """Records each credit pack purchase made via Stripe."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="credit_purchases",
    )
    credits = models.PositiveIntegerField(help_text="Number of credits purchased")
    amount_cents = models.PositiveIntegerField(help_text="Amount charged in cents")
    currency = models.CharField(max_length=3, default="usd")
    stripe_session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} +{self.credits} credits (${self.amount_cents / 100:.2f})"
