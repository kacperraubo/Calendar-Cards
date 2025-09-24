from django.contrib import admin

from .models import Accounts, Settings


class AccountsAdmin(admin.ModelAdmin):
    list_display = ("email",)
    list_filter = ("email",)
    search_fields = ("email",)


class SettingsAdmin(admin.ModelAdmin):
    list_display = ("user",)


admin.site.register(Accounts, AccountsAdmin)
admin.site.register(Settings, SettingsAdmin)
