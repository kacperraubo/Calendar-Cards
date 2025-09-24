from django.contrib import admin

from .models import Availability, Event


class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "owner")
    list_filter = ("owner",)
    search_fields = ("title",)


class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ("starting_time", "ending_time")


admin.site.register(Event, EventAdmin)
admin.site.register(Availability, AvailabilityAdmin)
