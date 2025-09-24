import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


def get_token():
    return secrets.token_urlsafe(16)


class Accounts(AbstractBaseUser):

    email = models.EmailField(max_length=255, unique=True)
    confirmation_code = models.IntegerField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_external = models.BooleanField(default=False)

    objects = BaseUserManager()

    USERNAME_FIELD = "email"

    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True
        return False

    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True
        return False


class Settings(models.Model):
    user = models.ForeignKey(
        Accounts, on_delete=models.CASCADE, related_name="settings"
    )
    token = models.CharField(max_length=100, default=get_token)
    time_zone = models.CharField(max_length=100, default=settings.TIME_ZONE)
