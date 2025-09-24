from django.urls import path

from . import views

urlpatterns = [
    path("sign-up", views.SignUpView.as_view(), name="sign_up"),
    path("sign-in", views.SignInView.as_view(), name="sign_in"),
    path("logout", views.LogoutView.as_view(), name="logout_view"),
    path(
        "email-confirmation",
        views.EmailConfirmationView.as_view(),
        name="email_confirmation_view",
    ),
    path(
        "<str:user_token>/settings",
        views.SetUserSettings.as_view(),
        name="set_user_settings",
    ),
]
