from django.shortcuts import render
from django.views.generic import View

from utilities.generate_meta_tags import generate_meta_tags


class TermsOfUseView(View):
    tou_template = "tou.html"

    def get(self, request):
        meta_tags = generate_meta_tags(
            "Terms of Use",
            "Terms of Use of our services.",
            request.build_absolute_uri("terms_of_use_view"),
        )

        context = {"meta_tags": meta_tags}
        return render(request, self.tou_template, context)


class PrivacyPolicyView(View):
    privacy_policy_template = "privacy_policy.html"

    def get(self, request):
        meta_tags = generate_meta_tags(
            "Privacy Policy",
            "Privacy Policy of our services.",
            request.build_absolute_uri("privacy_policy_view"),
        )

        context = {"meta_tags": meta_tags}
        return render(request, self.privacy_policy_template, context)
