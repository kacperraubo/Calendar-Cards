import datetime
import json

import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.forms import ValidationError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import View
from django.views.generic.edit import FormView

from account.forms import EmailConfirmation, SignInForm, SignUpForm, TimeZoneForm
from account.models import Accounts, Settings
from diary.models import Section
from utilities.generate_meta_tags import generate_meta_tags
from utilities.tasks import send_admin_notification, send_user_notification
from utilities.time import is_timezone_valid


class SignUpView(FormView):
    sign_up_template = "sign_up.html"
    user_new_account_template = "user_new_account_notification.html"
    admin_new_account_template = "admin_new_account_notification.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")

        form = SignUpForm()

        meta_tags = generate_meta_tags(
            "Calendar Cards · Sign Up",
            "A web-based calendar.",
            request.build_absolute_uri(reverse("sign_up")),
        )

        context = {
            "meta_tags": meta_tags,
            "form": form,
        }
        return render(request, self.sign_up_template, context)

    def post(self, request):
        form = SignUpForm(data=request.POST)

        if form.is_valid():
            new_account = form.save(commit=False)
            new_account.set_password(form.cleaned_data.get("password"))
            new_account.confirmation_code = form._generate_confirmation_code()

            try:
                new_account.save()

                if not Settings.objects.filter(user=new_account).exists():
                    Settings.objects.create(
                        user=new_account, time_zone=form.cleaned_data.get("timezone")
                    )

            except Exception:
                form.add_error(
                    field=None,
                    error=ValidationError(
                        "We couldn't create your account. Contact administrator."
                    ),
                )
                new_account = None

            if new_account:
                notification_context = {
                    "confirmation_code": new_account.confirmation_code,
                    "account_email": new_account.email,
                }
                send_user_notification.delay(
                    notification_context,
                    f"Calendar Cards — Activate your account: {new_account.confirmation_code}",
                    self.user_new_account_template,
                    [new_account.email],
                )

                send_admin_notification.delay(
                    notification_context,
                    "Calendar Cards — New account has been registered",
                    self.admin_new_account_template,
                )

                request.session["confirming_account_id"] = new_account.id
                return redirect("email_confirmation_view")

        meta_tags = generate_meta_tags(
            "Calendar Cards · Sign Up",
            "A web-based calendar.",
            request.build_absolute_uri(reverse("sign_up")),
        )

        context = {
            "form": form,
            "meta_tags": meta_tags,
        }
        return render(request, self.sign_up_template, context)


class SignInView(FormView):
    sign_in_template = "sign_in.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")

        form = SignInForm()

        meta_tags = generate_meta_tags(
            "Calendar Cards · Login",
            "A web-based calendar.",
            request.build_absolute_uri(reverse("sign_in")),
        )

        context = {
            "form": form,
            "meta_tags": meta_tags,
        }

        return render(request, self.sign_in_template, context)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("home")

        form = SignInForm(data=request.POST)
        if form.is_valid():
            if Accounts.objects.filter(email=form.cleaned_data["email"]).exists():
                account = Accounts.objects.get(email=form.cleaned_data["email"])
            elif Accounts.objects.filter(
                email=form.cleaned_data["email"], is_superuser=True
            ).exists():
                account = Accounts.objects.get(
                    email=form.cleaned_data["email"], is_superuser=True
                )

            if account.confirmation_code and not account.is_active:
                request.session["confirming_account_id"] = account.id
                return redirect("email_confirmation_view")

            account = authenticate(
                request,
                username=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            if account:
                login(request, account)
                return redirect("home")

            form.add_error(
                field=None, error=ValidationError("Wrong e-mail address or password")
            )

        meta_tags = generate_meta_tags(
            "Calendar Cards · Login",
            "A web-based calendar.",
            request.build_absolute_uri(reverse("sign_in")),
        )

        context = {
            "form": form,
            "meta_tags": meta_tags,
        }
        return render(request, self.sign_in_template, context)


class LogoutView(View):
    def get(self, request):
        account = request.user
        if not account.is_authenticated:
            return redirect("home")

        logout(request)
        return redirect("home")


class EmailConfirmationView(View):
    email_confirmation_template = "email_confirmation.html"

    def get(self, request):
        if request.session.get("confirming_account_id") is None:
            return redirect("sign_in")
        get_object_or_404(Accounts, id=request.session.get("confirming_account_id"))
        form = EmailConfirmation()

        meta_tags = generate_meta_tags(
            "Calendar Cards · Email Confirmation",
            "A web-based calendar.",
            request.build_absolute_uri(reverse("email_confirmation_view")),
        )

        context = {"form": form, "meta_tags": meta_tags}
        return render(request, self.email_confirmation_template, context)

    def post(self, request):
        account = Accounts.objects.get(id=request.session["confirming_account_id"])
        form = EmailConfirmation(
            data=request.POST, account_id=request.session.get("confirming_account_id")
        )

        if form.is_valid():
            account.confirmation_code = None
            if not account.is_active:
                account.is_active = True
            account.save()
            if "confirming_account_id" in request.session:
                del request.session["confirming_account_id"]
            login(request, account)
            if not Settings.objects.filter(user=account).exists():
                user_settings = Settings.objects.create(user=account)
                user_time_zone = request.POST.get("timezone")
                if is_timezone_valid(user_time_zone):
                    user_settings.time_zone = user_time_zone
                    user_settings.save()

            if not Section.objects.filter(user=account).exists():
                Section.objects.create(user=account, name="General")

            return redirect("home")

        meta_tags = generate_meta_tags(
            "Calendar Cards · Email Confirmation",
            "A web-based calendar.",
            request.build_absolute_uri(reverse("email_confirmation_view")),
        )

        context = {"form": form, "meta_tags": meta_tags}

        return render(request, self.email_confirmation_template, context)


class SetUserSettings(View):
    template_name = "user_settings.html"

    def get(self, request, user_token):
        try:
            user_settings = Settings.objects.get(token=user_token)
        except Settings.DoesNotExist:
            raise Http404("Not found")

        meta_tags = generate_meta_tags(
            "Calendar Cards · User Settings",
            "Your Calendar.",
            request.build_absolute_uri(reverse("set_user_settings", args=[user_token])),
        )

        form = TimeZoneForm(initial={"time_zone": user_settings.time_zone})
        context = {
            "form": form,
            "current_time_zone": user_settings.time_zone,
            "meta_tags": meta_tags,
            "user_token": user_token,
        }

        return render(request, self.template_name, context)

    def post(self, request, user_token):

        form = TimeZoneForm(data=request.POST)
        user_settings = get_object_or_404(Settings, token=user_token)

        if form.is_valid():
            if form.has_changed():
                new_time_zone = form.cleaned_data.get("time_zone")
                user_settings.time_zone = new_time_zone
                user_settings.save()

            return redirect("home")

        meta_tags = generate_meta_tags(
            "Calendar Cards · User Settings",
            "Your Calendar.",
            request.build_absolute_uri(
                reverse("set_user_settings", args=[user_settings.token])
            ),
        )

        context = {"form": form, "meta_tags": meta_tags}

        return render(request, self.template_name, context)
