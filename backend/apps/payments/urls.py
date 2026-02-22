from django.urls import path

from .views import CreateCheckoutView, stripe_webhook

urlpatterns = [
    path("checkout/", CreateCheckoutView.as_view(), name="checkout"),
    path("webhook/", stripe_webhook, name="stripe-webhook"),
]
