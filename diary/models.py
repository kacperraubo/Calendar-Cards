from __future__ import annotations

import datetime
import json
import secrets
import typing

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse

from account.models import Accounts
from utilities.tasks import send_user_notification
from utilities.time import time_slots


def get_token():
    return secrets.token_urlsafe(16)


class EventReminderType(models.TextChoices):
    WEEK_BEFORE = "week_before", "One week before"
    DAY_BEFORE = "day_before", "One day before"
    _12_HOURS_BEFORE = "12_hours_before", "12 hours before"
    _6_HOURS_BEFORE = "6_hours_before", "6 hours before"
    HOUR_BEFORE = "hour_before", "One hour before"
    _30_MINUTES_BEFORE = "30_minutes_before", "30 minutes before"
    _15_MINUTES_BEFORE = "15_minutes_before", "15 minutes before"
    MINUTE_BEFORE = "minute_before", "One minute before"


class Event(models.Model):
    token = models.CharField(max_length=100, default=get_token)
    owner = models.ForeignKey(Accounts, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=120)
    description = models.TextField(null=True, blank=True)
    dates = ArrayField(models.DateField())
    starting_time = models.TimeField(null=True, blank=True)
    ending_time = models.TimeField(null=True, blank=True)
    meeting_location = models.CharField(max_length=250, null=True, blank=True)
    anonymous_guests = ArrayField(models.EmailField(), default=list)
    section = models.ForeignKey(
        "Section",
        on_delete=models.CASCADE,
        related_name="events",
    )
    reminders = ArrayField(
        models.CharField(max_length=20, choices=EventReminderType.choices),
        default=list,
    )

    @property
    def stringified_dates(self):
        return self.stringify_dates()

    @property
    def invited_users(self):
        return [invitation.user for invitation in self.invitations.all()]

    @property
    def accepted_invitations(self):
        return self.invitations.filter(accepted=True)

    @property
    def pending_invitations(self):
        return self.invitations.filter(accepted=False)

    def __str__(self):
        return f"{self.title} event of {self.user.email}"

    def delete(self, using=None, keep_parents=False):
        emails_to_notify = [
            invitation.user.email for invitation in self.accepted_invitations
        ] + self.anonymous_guests

        context = {
            "event_title": self.title,
            "event_description": self.description,
            "event_dates": self.stringify_dates(separator=", "),
            "event_starting_time": self.starting_time,
            "event_ending_time": self.ending_time,
        }

        send_user_notification.delay(
            context,
            f"Calendar Cards — {self.title}",
            "diary/email/event_deletion.html",
            emails_to_notify,
        )

        return super().delete(using, keep_parents)

    def stringify_dates(self, separator: str = ",", date_format: str = "%Y-%m-%d"):
        return separator.join([date.strftime(date_format) for date in self.dates])

    def send_anonymous_invitation_email(self, email: str):
        context = {
            "event_owner_email": self.owner.email,
            "event_title": self.title,
            "event_description": self.description,
            "event_starting_time": self.starting_time,
            "event_ending_time": self.ending_time,
            "event_dates": self.stringify_dates(separator=", "),
            "event_url": settings.ABSOLUTE_URL
            + reverse("event_details", args=[self.token]),
        }

        send_user_notification.delay(
            context,
            f"Calendar Cards — {self.title}",
            "diary/email/anonymous_event_invitation.html",
            [email],
        )

    def send_update_email(self):
        emails = [
            invitation.user.email for invitation in self.accepted_invitations
        ] + self.anonymous_guests

        context = {
            "event_title": self.title,
            "event_description": self.description,
            "event_starting_time": self.starting_time,
            "event_ending_time": self.ending_time,
            "event_dates": self.stringify_dates(separator=", "),
            "event_url": settings.ABSOLUTE_URL
            + reverse("event_details", args=[self.token]),
        }

        send_user_notification.delay(
            context,
            f"Calendar Cards — {self.title}",
            "diary/email/event_update.html",
            emails,
        )


class EventInvitation(models.Model):
    token = models.CharField(max_length=100, default=get_token)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="invitations"
    )
    user = models.ForeignKey(
        Accounts, on_delete=models.CASCADE, related_name="invitations"
    )
    accepted = models.BooleanField(default=False)
    section = models.ForeignKey(
        "Section",
        on_delete=models.CASCADE,
        related_name="event_invitations",
        null=True,
        blank=True,
    )
    reminders = ArrayField(
        models.CharField(max_length=20, choices=EventReminderType.choices),
        default=list,
    )

    def __str__(self):
        return f"Event invitation for {self.event.title} to {self.user.email}"

    def send_invitation_email(self):
        context = {
            "event_owner_email": self.event.owner.email,
            "event_title": self.event.title,
            "event_description": self.event.description,
            "event_starting_time": self.event.starting_time,
            "event_ending_time": self.event.ending_time,
            "event_dates": self.event.stringify_dates(separator=", "),
            "invitation_url": settings.ABSOLUTE_URL + reverse("view_invitations"),
        }

        send_user_notification.delay(
            context,
            f"Calendar Cards — {self.event.title}",
            "diary/email/event_invitation.html",
            [self.user.email],
        )


class AvailabilityTimeSlot(models.Model):
    token = models.CharField(max_length=100, default=get_token)
    availability = models.ForeignKey(
        "Availability", on_delete=models.CASCADE, related_name="time_slots"
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.availability.user.email} availability time slot"


class Availability(models.Model):
    token = models.CharField(max_length=100, default=get_token)
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    starting_time = models.TimeField(null=True, blank=True)
    ending_time = models.TimeField(null=True, blank=True)
    date = models.DateField()
    section = models.ForeignKey(
        "Section", on_delete=models.CASCADE, related_name="availabilities"
    )

    @property
    def jsonified_time_slots(self) -> typing.List[typing.Dict[str, str]]:
        return json.dumps(
            [
                {
                    "token": time_slot.token,
                    "start": time_slot.start_time.strftime("%H:%M"),
                    "end": time_slot.end_time.strftime("%H:%M"),
                }
                for time_slot in self.time_slots.all()
            ]
        )

    @property
    def adjacent_time_slots(self) -> typing.List[AvailabilityTimeSlot]:
        slots = [[]]
        current_index = 0

        for time_slot in time_slots:
            if self.time_slots.filter(
                start_time=time_slot.start, end_time=time_slot.end
            ).exists():
                slots[current_index].append(time_slot)
            else:
                if len(slots[current_index]) > 0:
                    current_index += 1
                    slots.append([])

        return slots

    @property
    def adjacent_available_time_slots(
        self,
    ) -> typing.List[typing.List[AvailabilityTimeSlot]]:
        slots = [[]]
        current_index = 0

        for time_slot in time_slots:
            if self.time_range_is_available(time_slot.start, time_slot.end):
                slots[current_index].append(time_slot)
            else:
                if len(slots[current_index]) > 0:
                    current_index += 1
                    slots.append([])

        return slots

    @property
    def has_available_time_slot(self) -> bool:
        for time_slot in time_slots:
            if self.time_range_is_available(time_slot.start, time_slot.end):
                return True

        return False

    @property
    def has_vacant_time_slot(self) -> bool:
        for time_slot in time_slots:
            if self.time_range_is_vacant(time_slot.start, time_slot.end):
                return True

        return False

    def time_range_is_vacant(
        self, start_time: datetime.time, end_time: datetime.time
    ) -> bool:
        if end_time == datetime.time(0, 0):
            end_time = datetime.time(23, 59, 59, 999)

        for time_slot in self.time_slots.all():
            end = (
                datetime.time(23, 59, 59, 999)
                if time_slot.end_time == datetime.time(0, 0)
                else time_slot.end_time
            )

            if time_slot.start_time <= start_time < end:
                return False

            if time_slot.start_time < end_time <= end:
                return False

        return True

    def time_range_is_available(
        self, start_time: datetime.time, end_time: datetime.time
    ) -> bool:
        if self.time_range_is_vacant(start_time, end_time):
            return False

        for event in self.events.all():
            if event.start_time <= start_time < event.end_time:
                return False

            if event.start_time < end_time <= event.end_time:
                return False

        return True

    def __str__(self):
        return f"{self.user.email} availability on {self.date}"


class AvailabilityEvent(models.Model):
    token = models.CharField(max_length=100, default=get_token)
    creator = models.EmailField()
    availability = models.ForeignKey(
        Availability, on_delete=models.CASCADE, related_name="events"
    )
    title = models.CharField(max_length=120)
    description = models.TextField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    address = models.CharField(max_length=250)
    reminders = ArrayField(
        models.CharField(max_length=20, choices=EventReminderType.choices),
        default=list,
    )

    @property
    def starting_time(self) -> datetime.time:
        return self.start_time

    @property
    def ending_time(self) -> datetime.time:
        return self.end_time

    @property
    def meeting_location(self) -> str:
        return self.address


class Section(models.Model):
    token = models.CharField(max_length=100, default=get_token)
    user = models.ForeignKey(
        Accounts, on_delete=models.CASCADE, related_name="sections"
    )
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.name} section of {self.user.email}"
