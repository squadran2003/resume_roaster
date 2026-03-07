from django.urls import path

from .views import CreateCheckoutView, CreditCheckoutView, CreditPacksView, stripe_webhook

urlpatterns = [
    path("checkout/", CreateCheckoutView.as_view(), name="checkout"),
    path("credits/packs/", CreditPacksView.as_view(), name="credit-packs"),
    path("credits/checkout/", CreditCheckoutView.as_view(), name="credit-checkout"),
    path("webhook/", stripe_webhook, name="stripe-webhook"),
]
