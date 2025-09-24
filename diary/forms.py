import typing
import datetime

from django import forms
from django.core.validators import EmailValidator

from account.models import Accounts
from utilities.forms import StringListField
from utilities.time import half_hour_intervals, time_slots

from .models import (
    Availability,
    Event,
    Section,
    EventInvitation,
    AvailabilityEvent,
    EventReminderType,
    AvailabilityTimeSlot,
)


def clean_start_and_end_time(start_time: datetime.time, end_time: datetime.time):
    if start_time not in [interval.time() for interval in half_hour_intervals]:
        raise forms.ValidationError("Start time must be in half-hour intervals.")

    if end_time not in [interval.time() for interval in half_hour_intervals]:
        raise forms.ValidationError("End time must be in half-hour intervals.")

    if start_time >= end_time:
        raise forms.ValidationError("End time must be later than start time.")


class RemindersMixin(forms.Form):
    reminders = StringListField(required=False)

    def clean_reminders(self) -> typing.List[str]:
        cleaned_data = self.cleaned_data

        reminders = cleaned_data.get("reminders")

        for reminder in reminders:
            if reminder not in EventReminderType.values:
                raise forms.ValidationError("Invalid reminder type.")

        if len(set(reminders)) != len(reminders):
            raise forms.ValidationError("You cannot provide the same reminder twice.")

        return reminders


class BaseEventForm(RemindersMixin):
    title = forms.CharField(widget=forms.TextInput())
    description = forms.CharField(required=False, strip=True)
    guests = StringListField()
    address = forms.CharField(required=False)
    dates = StringListField()
    start_time = forms.TimeField(required=False)
    end_time = forms.TimeField(required=False)

    _require_dates = True

    def __init__(self, *args: typing.Any, user: Accounts, **kwargs: typing.Any):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()

        start_time: typing.Optional[datetime.time] = cleaned_data.get("start_time")
        end_time: typing.Optional[datetime.time] = cleaned_data.get("end_time")

        if start_time and not end_time or end_time and not start_time:
            raise forms.ValidationError("You have to provide both start and end time.")

        if start_time and end_time:
            clean_start_and_end_time(start_time, end_time)

        return cleaned_data

    def clean_dates(self) -> typing.List[str]:
        cleaned_data = self.cleaned_data

        dates = cleaned_data.get("dates")

        if self._require_dates:
            if len(dates) < 1:
                raise forms.ValidationError("You have to provide at least one date.")

        for date in dates:
            try:
                datetime.datetime.strptime(date, "%Y-%m-%d")
            except (ValueError, TypeError):
                raise forms.ValidationError("Dates must be in format YYYY-MM-DD.")

        return dates

    def clean_guests(self) -> typing.List[str]:
        email_validator = EmailValidator()

        cleaned_data = self.cleaned_data

        guests = cleaned_data.get("guests")

        for index, guest in enumerate(guests):
            guest = guest.strip()

            try:
                email_validator(guest)
            except forms.ValidationError:
                raise forms.ValidationError(f"Invalid email address: {guest}")

            account = Accounts.objects.filter(email=guest).first()

            if account == self.user:
                raise forms.ValidationError("You cannot invite yourself.")

            guests[index] = guest

        return guests


class CreateEventForm(BaseEventForm):
    section = forms.CharField(error_messages={"required": "Section is required."})

    def __init__(self, *args: typing.Any, user: Accounts, **kwargs: typing.Any):
        super().__init__(*args, **kwargs, user=user)
        self.user = user

    def clean_section(self) -> str:
        cleaned_data = self.cleaned_data

        section = cleaned_data.get("section")

        if not Section.objects.filter(token=section, user=self.user).exists():
            raise forms.ValidationError("Section does not exist.")

        return section

    def save(self) -> Event:
        section = Section.objects.get(
            token=self.cleaned_data.get("section"), user=self.user
        )
        title: str = self.cleaned_data.get("title")
        description: str = self.cleaned_data.get("description")
        guests: typing.List[str] = self.cleaned_data.get("guests")
        address: str = self.cleaned_data.get("address")
        dates: typing.List[str] = self.cleaned_data.get("dates")
        start_time: typing.Optional[datetime.time] = self.cleaned_data.get("start_time")
        end_time: typing.Optional[datetime.time] = self.cleaned_data.get("end_time")
        reminders: typing.List[str] = self.cleaned_data.get("reminders")

        dates = [datetime.datetime.strptime(date, "%Y-%m-%d").date() for date in dates]

        event = Event.objects.create(
            owner=self.user,
            title=title,
            description=description,
            dates=dates,
            starting_time=start_time,
            ending_time=end_time,
            meeting_location=address,
            section=section,
            reminders=reminders,
        )

        for guest in guests:
            if (account := Accounts.objects.filter(email=guest).first()) is not None:
                invitation = EventInvitation.objects.create(event=event, user=account)
                invitation.send_invitation_email()
            else:
                event.anonymous_guests.append(guest)
                event.send_anonymous_invitation_email(guest)

            event.save()

        return event


class EditEventForm(CreateEventForm):
    token = forms.CharField()
    deleted_dates = StringListField()
    event: Event

    _require_dates = False

    def clean_token(self) -> str:
        token = self.cleaned_data.get("token")

        event = Event.objects.filter(token=token, owner=self.user).first()

        if event is None:
            raise forms.ValidationError("Event with this token does not exist.")

        self.event = event

        return token

    def clean_deleted_dates(self) -> typing.List[str]:
        cleaned_data = self.cleaned_data

        deleted_dates: typing.List[datetime.date] = cleaned_data.get("deleted_dates")

        for date in deleted_dates:
            try:
                datetime.datetime.strptime(date, "%Y-%m-%d")
            except (ValueError, TypeError):
                raise forms.ValidationError("Dates must be in format YYYY-MM-DD.")

        return deleted_dates

    def save(self) -> Event:
        event = self.event
        section = Section.objects.get(
            token=self.cleaned_data.get("section"), user=self.user
        )

        event.title = self.cleaned_data.get("title")
        event.description = self.cleaned_data.get("description")
        event.starting_time = self.cleaned_data.get("start_time")
        event.ending_time = self.cleaned_data.get("end_time")
        event.meeting_location = self.cleaned_data.get("address")
        event.reminders = self.cleaned_data.get("reminders")
        event.section = section

        event.save()

        dates = [
            datetime.datetime.strptime(date, "%Y-%m-%d").date()
            for date in self.cleaned_data.get("dates")
        ]
        deleted_dates = [
            datetime.datetime.strptime(date, "%Y-%m-%d").date()
            for date in self.cleaned_data.get("deleted_dates")
        ]

        for date in dates:
            if date not in event.dates:
                event.dates.append(date)

            event.save()

        for date in deleted_dates:
            if date in event.dates:
                event.dates.remove(date)

            event.save()

        event.send_update_email()

        guests = self.cleaned_data.get("guests")

        for guest in guests:
            if (account := Accounts.objects.filter(email=guest).first()) is not None:
                invitation, created = EventInvitation.objects.get_or_create(
                    event=event, user=account
                )

                if created:
                    invitation.send_invitation_email()
            else:
                if guest not in event.anonymous_guests:
                    event.anonymous_guests.append(guest)
                    event.send_anonymous_invitation_email(guest)

            event.save()

        return event


class AddSectionForm(forms.Form):
    name = forms.CharField(error_messages={"required": "Name is required."})

    def __init__(self, *args: typing.Any, user: Accounts, **kwargs: typing.Any):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_name(self) -> str:
        name: str = self.cleaned_data.get("name")

        if Section.objects.filter(name=name, user=self.user).exists():
            raise forms.ValidationError("Section with this name already exists.")

        return name

    def save(self) -> Section:
        name = self.cleaned_data.get("name")

        return Section.objects.create(name=name, user=self.user)


class RespondToEventInvitationForm(forms.Form):
    invitation_token = forms.CharField(
        error_messages={"required": "Token is required."}
    )
    accept = forms.BooleanField(required=False)
    section = forms.CharField(required=False, strip=True)
    invitation: EventInvitation

    def __init__(self, *args: typing.Any, user: Accounts, **kwargs: typing.Any):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_invitation_token(self) -> str:
        invitation_token = self.cleaned_data.get("invitation_token")

        self.invitation = EventInvitation.objects.filter(
            token=invitation_token, user=self.user
        ).first()

        if self.invitation is None:
            raise forms.ValidationError("Invitation does not exist.")

        return invitation_token

    def clean_section(self) -> str:
        if not self.cleaned_data.get("accept"):
            return None

        section = self.cleaned_data.get("section")

        if not Section.objects.filter(token=section, user=self.user).exists():
            raise forms.ValidationError("Section does not exist.")

        return section

    def save(self) -> EventInvitation:
        if self.cleaned_data.get("accept"):
            section = Section.objects.get(
                token=self.cleaned_data.get("section"), user=self.user
            )

            self.invitation.accepted = True
            self.invitation.section = section
            self.invitation.save()
        else:
            self.invitation.delete()

        return self.invitation


class CreateEventForAvailabilityForm(forms.Form):
    token = forms.CharField(error_messages={"required": "Token is required."})
    title = forms.CharField(error_messages={"required": "Title is required."})
    description = forms.CharField(required=False, strip=True)
    email = forms.EmailField(error_messages={"required": "Email is required."})
    start_time = forms.TimeField(error_messages={"required": "Start time is required."})
    end_time = forms.TimeField(error_messages={"required": "End time is required."})
    address = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super().clean()

        start_time: datetime.time = cleaned_data.get("start_time")
        end_time: datetime.time = cleaned_data.get("end_time")

        clean_start_and_end_time(start_time, end_time)

        if not self.availability.time_range_is_available(start_time, end_time):
            raise forms.ValidationError("Time range is not available.")

        return cleaned_data

    def clean_token(self) -> str:
        token = self.cleaned_data.get("token")

        self.availability = Availability.objects.filter(token=token).first()

        if self.availability is None:
            raise forms.ValidationError("Availability does not exist.")

        if not self.availability.has_available_time_slot:
            raise forms.ValidationError("There are no available time slots.")

        return token

    def save(self) -> AvailabilityEvent:
        return AvailabilityEvent.objects.create(
            creator=self.cleaned_data.get("email"),
            availability=self.availability,
            title=self.cleaned_data.get("title"),
            description=self.cleaned_data.get("description"),
            start_time=self.cleaned_data.get("start_time"),
            end_time=self.cleaned_data.get("end_time"),
            address=self.cleaned_data.get("address"),
        )


class EditAcceptedInvitationForm(RemindersMixin):
    token = forms.CharField(error_messages={"required": "Token is required."})
    section = forms.CharField(error_messages={"required": "Section is required."})

    def __init__(self, *args: typing.Any, user: Accounts, **kwargs: typing.Any):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_token(self) -> str:
        token = self.cleaned_data.get("token")

        self.invitation = EventInvitation.objects.filter(
            token=token, user=self.user, accepted=True
        ).first()

        if self.invitation is None:
            raise forms.ValidationError("Invitation does not exist.")

        return token

    def clean_section(self) -> str:
        section = self.cleaned_data.get("section")

        if not Section.objects.filter(token=section, user=self.user).exists():
            raise forms.ValidationError("Section does not exist.")

        return section

    def save(self) -> EventInvitation:
        reminders = self.cleaned_data.get("reminders")

        section = Section.objects.get(
            token=self.cleaned_data.get("section"), user=self.user
        )

        self.invitation.section = section
        self.invitation.reminders = reminders
        self.invitation.save()

        return self.invitation


class AddAvailabilityTimeSlotForm(forms.Form):
    section = forms.CharField(error_messages={"required": "Section is required."})
    date = forms.DateField(error_messages={"required": "Date is required."})
    start_time = forms.TimeField(error_messages={"required": "Start time is required."})
    end_time = forms.TimeField(error_messages={"required": "End time is required."})

    def __init__(self, *args: typing.Any, user: Accounts, **kwargs: typing.Any):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()

        start_time: datetime.time = cleaned_data.get("start_time")
        end_time: datetime.time = cleaned_data.get("end_time")

        if (start_time, end_time) not in [
            (slot.start, slot.end) for slot in time_slots
        ]:
            raise forms.ValidationError("Invalid time slot.")

        return cleaned_data

    def clean_section(self) -> str:
        section = self.cleaned_data.get("section")

        if not Section.objects.filter(token=section, user=self.user).exists():
            raise forms.ValidationError("Section does not exist.")

        return section

    def save(self) -> AvailabilityTimeSlot:
        section = Section.objects.get(
            token=self.cleaned_data.get("section"), user=self.user
        )

        availability = Availability.objects.filter(
            section=section, date=self.cleaned_data.get("date")
        ).first()

        if availability is None:
            availability = Availability.objects.create(
                user=self.user,
                section=section,
                date=self.cleaned_data.get("date"),
            )

        return AvailabilityTimeSlot.objects.create(
            availability=availability,
            start_time=self.cleaned_data.get("start_time"),
            end_time=self.cleaned_data.get("end_time"),
        )


class EditAvailabilityEventForm(RemindersMixin):
    token = forms.CharField(error_messages={"required": "Token is required."})

    def __init__(self, *args: typing.Any, user: Accounts, **kwargs: typing.Any):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_token(self) -> str:
        token = self.cleaned_data.get("token")

        self.event = AvailabilityEvent.objects.filter(
            token=token, availability__user=self.user
        ).first()

        if self.event is None:
            raise forms.ValidationError("Event does not exist.")

        return token

    def save(self) -> AvailabilityEvent:
        reminders = self.cleaned_data.get("reminders")

        self.event.reminders = reminders
        self.event.save()

        return self.event
