from django.urls import path

from . import views

urlpatterns = [
    path("terms-of-use", views.TermsOfUseView.as_view(), name="terms_of_use_view"),
    path(
        "privacy-policy", views.PrivacyPolicyView.as_view(), name="privacy_policy_view"
    ),
]
