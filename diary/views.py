import calendar
import json
import typing
from datetime import date, datetime, time, timedelta

import pytz
from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from account.models import Settings
from utilities.generate_meta_tags import generate_meta_tags
from utilities.responses import (
    ApiErrorKwargsResponse,
    ApiFormErrorResponse,
    ApiSuccessKwargsResponse,
)
from utilities.time import (
    half_hour_intervals,
    time_slots,
)

from .forms import (
    AddAvailabilityTimeSlotForm,
    AddSectionForm,
    CreateEventForAvailabilityForm,
    CreateEventForm,
    EditAcceptedInvitationForm,
    EditAvailabilityEventForm,
    EditEventForm,
    RespondToEventInvitationForm,
)
from .models import (
    Availability,
    AvailabilityEvent,
    AvailabilityTimeSlot,
    Event,
    EventInvitation,
    EventReminderType,
    Section,
)

DISPLAY_MODE_SINGLE = "single"
DISPLAY_MODE_MULTI = "multi"
DISPLAY_MODE_YEAR = "year"
VALID_DISPLAY_MODES = {DISPLAY_MODE_SINGLE, DISPLAY_MODE_MULTI, DISPLAY_MODE_YEAR}


class DisplayModeView(View):
    def _get_display_mode(self) -> str:
        mode = self.request.GET.get("display-mode", DISPLAY_MODE_SINGLE)

        return mode if mode in VALID_DISPLAY_MODES else DISPLAY_MODE_SINGLE

    def _get_start_date(self) -> date:
        start_date = self.request.GET.get("start-date", None)

        if start_date:
            return datetime.strptime(start_date, "%Y-%m").date()

        return datetime.now(tz=self._get_user_timezone()).replace(day=1).date()

    def _get_user_timezone(self) -> pytz.timezone:
        if self.request.user.is_anonymous:
            return pytz.timezone("UTC")

        settings = get_object_or_404(Settings, user=self.request.user)

        return pytz.timezone(settings.time_zone)

    def _get_section(self, section_token: typing.Optional[str]):
        if section_token:
            return get_object_or_404(
                Section, token=section_token, user=self.request.user
            )

        return Section.objects.filter(user=self.request.user).first()

    def _calculate_end_date(self, start_date: date, display_mode: str) -> date:
        months_ahead = {
            DISPLAY_MODE_SINGLE: 0,
            DISPLAY_MODE_MULTI: 5,
            DISPLAY_MODE_YEAR: 11,
        }.get(display_mode, 0)

        end_date = start_date + relativedelta(months=months_ahead)
        _, last_day = calendar.monthrange(end_date.year, end_date.month)

        return end_date.replace(day=last_day)

    def _get_events(
        self, section: Section, date: date
    ) -> typing.List[typing.Union[Event, AvailabilityEvent]]:
        def sort_key(event: typing.Union[Event, AvailabilityEvent]) -> time:
            if isinstance(event, Event):
                return event.starting_time or datetime.min.time()

            return event.start_time

        return sorted(
            list(Event.objects.filter(section=section, dates__contains=[date]))
            + [
                invitation.event
                for invitation in EventInvitation.objects.filter(
                    accepted=True,
                    event__dates__contains=[date],
                    section=section,
                )
            ]
            + list(
                AvailabilityEvent.objects.filter(
                    availability__section=section,
                    availability__date=date,
                )
            ),
            key=sort_key,
        )

    def _generate_calendar_days(
        self,
        start_date: date,
        end_date: date,
        section: Section,
        user_timezone: pytz.timezone,
    ) -> typing.List[typing.Dict]:
        days = []
        current_date = start_date

        first_monday = self._get_first_monday(start_date)
        self._add_previous_month_days(days, start_date, first_monday)

        while current_date <= end_date:
            events = self._get_events(section, current_date)

            now = datetime.now(tz=user_timezone)

            has_event = len(events) > 0
            is_today = current_date == now.date()
            is_past = current_date < now.date()
            is_future = current_date > now.date()
            has_all_day_event = any(event.starting_time is None for event in events)

            has_past_event = (
                is_past
                and has_event
                or is_today
                and any(
                    event.ending_time and event.ending_time < now.time()
                    for event in events
                )
            )

            has_ongoing_event = (
                is_today
                and any(
                    event.starting_time
                    and event.starting_time <= now.time()
                    and event.ending_time >= now.time()
                    for event in events
                )
                or (has_all_day_event and is_today)
            )

            has_future_event = (
                is_future
                and has_event
                or is_today
                and any(
                    event.starting_time and event.starting_time > now.time()
                    for event in events
                )
            )

            days.append(
                {
                    "datetime": datetime.combine(current_date, datetime.min.time()),
                    "is_weekend": current_date.weekday() in {5, 6},
                    "is_previous_month": False,
                    "events": events,
                    "has_past_event": has_past_event,
                    "has_ongoing_event": has_ongoing_event,
                    "has_future_event": has_future_event,
                    "availability": Availability.objects.filter(
                        date=current_date,
                        section=section,
                    ).first(),
                    "notes": [],
                    **self._extend_day(
                        start_date=start_date,
                        end_date=end_date,
                        section=section,
                        user_timezone=user_timezone,
                        current_date=current_date,
                        events=events,
                    ),
                }
            )
            current_date += timedelta(days=1)

        return days

    def _extend_day(
        self,
        **kwargs: typing.Any,
    ) -> dict:
        return {}

    def _generate_monthly_calendar(
        self,
        start_date: datetime,
        end_date: datetime,
        section: Section,
        user_timezone: pytz.timezone,
    ) -> typing.List[typing.Dict]:
        months = []
        current_month = start_date

        while current_month <= end_date:
            months.append(
                {
                    "month": current_month,
                    "name": current_month.strftime("%B"),
                    "days": self._generate_calendar_days(
                        current_month.replace(day=1),
                        self._get_last_day_of_month(current_month),
                        section,
                        user_timezone,
                    ),
                }
            )
            current_month += relativedelta(months=1)

        return months

    @staticmethod
    def _get_first_monday(date: date) -> date:
        while date.weekday() != 0:
            date -= timedelta(days=1)

        return date

    @staticmethod
    def _get_last_day_of_month(date: date) -> date:
        _, last_day = calendar.monthrange(date.year, date.month)

        return date.replace(day=last_day)

    def _add_previous_month_days(
        self,
        days: typing.List[typing.Dict],
        start_date: date,
        first_monday: date,
    ) -> None:
        if first_monday < start_date:
            current_date = start_date - timedelta(days=1)

            while current_date >= first_monday:
                days.insert(
                    0,
                    {
                        "datetime": datetime.combine(current_date, datetime.min.time()),
                        "is_weekend": current_date.weekday() in {5, 6},
                        "is_previous_month": True,
                        "events": [],
                        "notes": [],
                    },
                )
                current_date -= timedelta(days=1)


class Home(DisplayModeView):
    template_name = "diary/home.html"

    def get(self, request: HttpRequest, section_token: typing.Optional[str] = None):
        if not request.user.is_authenticated:
            display_mode = self._get_display_mode()
            start_date = self._get_start_date()
            end_date = self._calculate_end_date(start_date, display_mode)

            context = {
                "now": datetime.now().date(),
                "today": datetime.now().date(),
                "display_mode": display_mode,
                "start_date": start_date,
                "end_date": end_date,
                "time_slots": time_slots,
                "meta_tags": self._generate_meta_tags(section_token),
            }

            if display_mode == DISPLAY_MODE_SINGLE:
                context["days"] = self._generate_calendar_days(
                    start_date, end_date, None, pytz.timezone("UTC")
                )
            else:
                context["months"] = self._generate_monthly_calendar(
                    start_date, end_date, None, pytz.timezone("UTC")
                )

            return render(request, self.template_name, context)

        display_mode = self._get_display_mode()
        section = self._get_section(section_token)
        user_timezone = self._get_user_timezone()
        start_date = self._get_start_date()
        end_date = self._calculate_end_date(start_date, display_mode)

        context = {
            "now": datetime.now(tz=user_timezone),
            "today": datetime.now(tz=user_timezone).date(),
            "section": section,
            "display_mode": display_mode,
            "start_date": start_date,
            "end_date": end_date,
            "user_time_zone": user_timezone,
            "time_slots": time_slots,
            "meta_tags": self._generate_meta_tags(section_token),
            "invitations": EventInvitation.objects.filter(
                user=request.user, accepted=False
            ),
        }

        if display_mode == DISPLAY_MODE_SINGLE:
            context["days"] = self._generate_calendar_days(
                start_date, end_date, section, user_timezone
            )
        else:
            context["months"] = self._generate_monthly_calendar(
                start_date, end_date, section, user_timezone
            )

        upcoming_event = self._get_upcoming_event(user_timezone, section)

        if upcoming_event:
            context["upcoming_event"] = upcoming_event

        return render(request, self.template_name, context)

    def _get_upcoming_event(
        self, user_timezone: pytz.timezone, section: Section
    ) -> typing.Optional[Event]:
        events_today = self._get_events(section, datetime.now(tz=user_timezone).date())

        for event in events_today:
            if (
                not event.starting_time
                or event.starting_time > datetime.now(tz=user_timezone).time()
            ):
                return event

    def _generate_meta_tags(self, section_token: typing.Optional[str]) -> dict:
        return generate_meta_tags(
            title="Calendar Cards",
            description="Your Calendar.",
            website_url=self.request.build_absolute_uri(
                reverse("home")
                if not section_token
                else reverse("home", args=[section_token])
            ),
        )


class CreateEvent(DisplayModeView):
    template_name = "diary/create_event.html"

    def get(self, request: HttpRequest):
        self.selected_days = self._get_selected_days()

        display_mode = self._get_display_mode()
        section = self._get_section(request.GET.get("section", None))
        user_timezone = self._get_user_timezone()
        start_date = self._get_start_date()
        end_date = self._calculate_end_date(start_date, display_mode)

        context = {
            "today": datetime.now(tz=user_timezone).date(),
            "section": section,
            "start_date": start_date,
            "end_date": end_date,
            "display_mode": display_mode,
            "user_time_zone": user_timezone,
            "selected_days": self.selected_days,
            "time_slots": time_slots,
            "reminder_options": EventReminderType.choices,
            "meta_tags": self._generate_meta_tags(),
        }

        if display_mode == DISPLAY_MODE_SINGLE:
            context["days"] = self._generate_calendar_days(
                start_date, end_date, section, user_timezone
            )
        else:
            context["months"] = self._generate_monthly_calendar(
                start_date, end_date, section, user_timezone
            )

        return render(request, self.template_name, context)

    def post(self, request: HttpRequest):
        form = CreateEventForm(json.loads(request.body), user=request.user)

        if not form.is_valid():
            return ApiFormErrorResponse(form)

        event = form.save()

        return ApiSuccessKwargsResponse(
            message="Event created successfully.",
            token=event.token,
        )

    def _generate_meta_tags(self) -> dict:
        return generate_meta_tags(
            title="Create Event",
            description="Create a new event.",
            website_url=self.request.build_absolute_uri(reverse("create_event")),
        )

    def _extend_day(
        self,
        current_date: datetime,
        **kwargs: typing.Any,
    ) -> dict:
        return {
            "is_selected": current_date in self.selected_days,
        }

    def _get_selected_days(self) -> typing.List[datetime.date]:
        days = self.request.GET.getlist("selected-days[]", None)

        if days is not None:
            try:
                return [datetime.strptime(day, "%Y-%m-%d").date() for day in days]
            except ValueError:
                return []

        return []


class AddSection(View):
    def post(self, request: HttpRequest):
        form = AddSectionForm(json.loads(request.body), user=request.user)

        if not form.is_valid():
            return ApiFormErrorResponse(form)

        section = form.save()

        return ApiSuccessKwargsResponse(
            message="Section added successfully.", token=section.token
        )


class DeleteSection(View):
    def post(self, request: HttpRequest, token: str):
        section = Section.objects.filter(user=request.user, token=token).first()

        if section is None:
            return ApiErrorKwargsResponse(message="Section not found.", token=token)

        if len(Section.objects.filter(user=request.user)) == 1:
            return ApiErrorKwargsResponse(
                message="You can't delete the last section.", token=token
            )

        section.delete()

        return ApiSuccessKwargsResponse(
            message="Section deleted successfully.",
            redirect=Section.objects.filter(user=request.user).first().token,
        )


class EditEvent(DisplayModeView):
    template_name = "diary/edit_event.html"

    def get(self, request: HttpRequest, token: str):
        event = get_object_or_404(Event, token=token)

        if event.owner == request.user:
            self.event = event
        else:
            invitation = get_object_or_404(
                EventInvitation, event=event, user=request.user, accepted=True
            )

            return redirect(
                reverse("edit_accepted_invitation", args=[invitation.token])
                + f"?{request.GET.urlencode()}"
            )

        self.selected_days = self._get_selected_days()

        display_mode = self._get_display_mode()
        user_timezone = self._get_user_timezone()
        start_date = self._get_start_date()
        end_date = self._calculate_end_date(start_date, display_mode)

        context = {
            "today": datetime.now(tz=user_timezone).date(),
            "display_mode": display_mode,
            "event": self.event,
            "section": self.event.section,
            "start_date": start_date,
            "end_date": end_date,
            "user_time_zone": user_timezone,
            "time_slots": time_slots,
            "reminder_options": EventReminderType.choices,
            "meta_tags": self._generate_meta_tags(token),
        }

        if display_mode == DISPLAY_MODE_SINGLE:
            context["days"] = self._generate_calendar_days(
                start_date, end_date, self.event.section, user_timezone
            )
        else:
            context["months"] = self._generate_monthly_calendar(
                start_date, end_date, self.event.section, user_timezone
            )

        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, token: str):
        form = EditEventForm(
            {
                "token": token,
                **json.loads(request.body),
            },
            user=request.user,
        )

        if not form.is_valid():
            return ApiFormErrorResponse(form)

        event = form.save()

        return ApiSuccessKwargsResponse(
            message="Event updated successfully.", redirect=event.section.token
        )

    def _get_selected_days(self) -> typing.List[datetime.date]:
        return list(self.event.dates)

    def _extend_day(
        self,
        current_date: datetime,
        **kwargs: typing.Any,
    ) -> dict:
        return {
            "is_selected": current_date in self.selected_days,
        }

    def _generate_meta_tags(self, token: str) -> dict:
        return generate_meta_tags(
            title="Edit Event",
            description="Edit an existing event.",
            website_url=self.request.build_absolute_uri(
                reverse("edit_event", args=[token])
            ),
        )


class DeleteEvent(View):
    def post(self, request: HttpRequest, token: str):
        event = Event.objects.filter(token=token, owner=request.user).first()

        if event is None:
            return ApiErrorKwargsResponse(message="Event not found.", token=token)

        section = event.section
        event.delete()

        return ApiSuccessKwargsResponse(
            message="Event deleted successfully.", redirect=section.name
        )


class RespondToEventInvitation(View):
    def post(self, request: HttpRequest, token: str):
        form = RespondToEventInvitationForm(
            {
                "event_token": token,
                **json.loads(request.body),
            },
            user=request.user,
        )

        if not form.is_valid():
            return ApiFormErrorResponse(form)

        form.save()

        return ApiSuccessKwargsResponse(message="Response saved successfully.")


class RemoveInvitation(View):
    def post(self, request: HttpRequest, token: str):
        invitation = EventInvitation.objects.filter(
            token=token, event__owner=request.user
        ).first()

        if invitation is None:
            return ApiErrorKwargsResponse(message="Invitation not found.")

        invitation.delete()

        return ApiSuccessKwargsResponse(message="User removed successfully.")


class RemoveAnonymousGuest(View):
    def post(self, request: HttpRequest, token: str, email: str):
        event = Event.objects.filter(token=token, owner=request.user).first()

        if event is None:
            return ApiErrorKwargsResponse(message="Event not found.", token=token)

        if email not in event.anonymous_guests:
            return ApiErrorKwargsResponse(
                message="Anonymous guest not found.", token=token
            )

        event.anonymous_guests.remove(email)
        event.save()

        return ApiSuccessKwargsResponse(message="Anonymous guest removed successfully.")


class Invitations(View):
    template_name = "diary/invitations.html"

    def get(self, request: HttpRequest):
        invitations = EventInvitation.objects.filter(user=request.user, accepted=False)

        context = {
            "invitations": invitations,
            "meta_tags": self._generate_meta_tags(),
        }

        return render(request, self.template_name, context)

    def _generate_meta_tags(self) -> dict:
        return generate_meta_tags(
            title="Invitations",
            description="Your event invitations.",
            website_url=self.request.build_absolute_uri(reverse("view_invitations")),
        )


class ExternalSectionView(DisplayModeView):
    template_name = "diary/external_section.html"

    def get(self, request: HttpRequest, token: str):
        section = get_object_or_404(Section, token=token)

        if section.user == request.user:
            return redirect(reverse("home", args=[token]))

        if section.availabilities.count() < 1:
            return redirect(reverse("home"))

        display_mode = self._get_display_mode()
        user_timezone = self._get_user_timezone()
        start_date = self._get_start_date()
        end_date = self._calculate_end_date(start_date, display_mode)

        context = {
            "today": datetime.now(tz=user_timezone).date(),
            "section": section,
            "display_mode": display_mode,
            "start_date": start_date,
            "end_date": end_date,
            "user_time_zone": user_timezone,
            "half_hour_intervals": half_hour_intervals,
            "meta_tags": self._generate_meta_tags(token),
        }

        if display_mode == DISPLAY_MODE_SINGLE:
            context["days"] = self._generate_calendar_days(
                start_date, end_date, section, user_timezone
            )
        else:
            context["months"] = self._generate_monthly_calendar(
                start_date, end_date, section, user_timezone
            )

        return render(request, self.template_name, context)

    def _generate_meta_tags(self, token: str) -> dict:
        return generate_meta_tags(
            title="Calendar Cards",
            description="Your Calendar.",
            website_url=self.request.build_absolute_uri(
                reverse("external_section", args=[token])
            ),
        )


class DayDetails(DisplayModeView):
    template_name = "diary/day_details.html"

    def get(self, request: HttpRequest, token: str, date: date):
        if not request.user.is_authenticated:
            return redirect(reverse("home"))

        self.date = date

        section = get_object_or_404(Section, token=token, user=request.user)
        events = Event.objects.filter(
            dates__contains=[date], owner=request.user, section=section
        )
        invitations = EventInvitation.objects.filter(
            user=request.user,
            accepted=True,
            event__dates__contains=[date],
            section=section,
        )
        availability = Availability.objects.filter(
            date=date, user=request.user, section=section
        ).first()
        availability_events = AvailabilityEvent.objects.filter(
            availability__date=date, availability__section=section
        )

        context = {
            "today": datetime.now(tz=self._get_user_timezone()).date(),
            "date": date,
            "events": events,
            "section": section,
            "invitations": invitations,
            "availability": availability,
            "availability_events": availability_events,
            "days": self._generate_calendar_days(
                date.replace(day=1),
                self._get_last_day_of_month(date),
                section,
                self._get_user_timezone(),
            ),
            "meta_tags": self._generate_meta_tags(token, date),
        }

        return render(request, self.template_name, context)

    def _extend_day(self, current_date: date, **kwargs: typing.Any) -> dict:
        return {
            "is_selected": current_date == self.date,
        }

    def _generate_meta_tags(self, token: str, date: date) -> dict:
        return generate_meta_tags(
            title=f"Calendar Cards - {date}",
            description="Your Calendar.",
            website_url=self.request.build_absolute_uri(
                reverse("day_details", args=[token, date])
            ),
        )


class EditAcceptedInvitation(EditEvent):
    template_name = "diary/edit_accepted_invitation.html"

    def get(self, request: HttpRequest, token: str):
        self.invitation = get_object_or_404(
            EventInvitation, token=token, user=request.user
        )
        self.event = self.invitation.event
        self.selected_days = self._get_selected_days()

        display_mode = self._get_display_mode()
        user_timezone = self._get_user_timezone()
        start_date = self._get_start_date()
        end_date = self._calculate_end_date(start_date, display_mode)

        context = {
            "invitation": self.invitation,
            "today": datetime.now(tz=user_timezone).date(),
            "display_mode": display_mode,
            "event": self.event,
            "section": self.invitation.section,
            "start_date": start_date,
            "end_date": end_date,
            "user_time_zone": user_timezone,
            "half_hour_intervals": half_hour_intervals,
            "reminder_options": EventReminderType.choices,
            "meta_tags": self._generate_meta_tags(token),
        }

        if display_mode == DISPLAY_MODE_SINGLE:
            context["days"] = self._generate_calendar_days(
                start_date, end_date, self.invitation.section, user_timezone
            )
        else:
            context["months"] = self._generate_monthly_calendar(
                start_date, end_date, self.invitation.section, user_timezone
            )

        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, token: str):
        form = EditAcceptedInvitationForm(
            {
                "token": token,
                **json.loads(request.body),
            },
            user=request.user,
        )

        if not form.is_valid():
            return ApiFormErrorResponse(form)

        invitation = form.save()

        return ApiSuccessKwargsResponse(
            message="Event updated successfully.", redirect=invitation.section.token
        )


class LeaveInvitation(View):
    def post(self, request: HttpRequest, token: str):
        invitation = EventInvitation.objects.filter(
            token=token, user=request.user
        ).first()
        section = invitation.section

        if invitation is None:
            return ApiErrorKwargsResponse(message="Invitation not found.", token=token)

        invitation.delete()

        return ApiSuccessKwargsResponse(
            message="Invitation deleted successfully.", redirect=section.token
        )


class EventDetails(EditEvent):
    template_name = "diary/event_details.html"

    def get(self, request: HttpRequest, token: str):
        self.event = get_object_or_404(Event, token=token)
        self.selected_days = self._get_selected_days()

        display_mode = self._get_display_mode()
        user_timezone = self._get_user_timezone()
        start_date = self._get_start_date()
        end_date = self._calculate_end_date(start_date, display_mode)

        context = {
            "today": datetime.now(tz=user_timezone).date(),
            "display_mode": display_mode,
            "event": self.event,
            "section": self.event.section,
            "start_date": start_date,
            "end_date": end_date,
            "user_time_zone": user_timezone,
            "half_hour_intervals": half_hour_intervals,
            "meta_tags": self._generate_meta_tags(token),
        }

        if display_mode == DISPLAY_MODE_SINGLE:
            context["days"] = self._generate_calendar_days(
                start_date, end_date, self.event.section, user_timezone
            )
        else:
            context["months"] = self._generate_monthly_calendar(
                start_date, end_date, self.event.section, user_timezone
            )

        return render(request, self.template_name, context)

    def _generate_meta_tags(self, token: str) -> dict:
        return generate_meta_tags(
            title="Event Details",
            description="Details of an event.",
            website_url=self.request.build_absolute_uri(
                reverse("event_details", args=[token])
            ),
        )


class ExternalAvailability(DisplayModeView):
    template_name = "diary/external_availability.html"

    def get(self, request: HttpRequest, token: str):
        self.availability = get_object_or_404(Availability, token=token)

        print(
            self.availability.has_available_time_slot,
            self.availability.has_vacant_time_slot,
        )

        if not self.availability.has_available_time_slot:
            return redirect(reverse("home"))

        if self.availability.user == request.user:
            return redirect(reverse("home"))

        display_mode = DISPLAY_MODE_SINGLE
        user_timezone = self._get_user_timezone()
        start_date = self.availability.date.replace(day=1)
        end_date = self._get_last_day_of_month(self.availability.date)

        context = {
            "today": datetime.now(tz=user_timezone).date(),
            "days": self._generate_calendar_days(
                start_date, end_date, self.availability.section, user_timezone
            ),
            "display_mode": display_mode,
            "availability": self.availability,
            "user_time_zone": user_timezone,
            "half_hour_intervals": half_hour_intervals,
            "meta_tags": self._generate_meta_tags(token),
        }

        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, token: str):
        data = {
            "token": token,
            **json.loads(request.body),
        }

        if request.user.is_authenticated:
            data["email"] = request.user.email

        form = CreateEventForAvailabilityForm(data)

        if not form.is_valid():
            return ApiFormErrorResponse(form)

        event = form.save()

        return ApiSuccessKwargsResponse(
            message="Event created successfully.",
            redirect=event.availability.section.token,
        )

    def _extend_day(self, current_date: date, **kwargs: typing.Any) -> dict:
        return {
            "is_selected": current_date == self.availability.date,
        }

    def _generate_meta_tags(self, token: str) -> dict:
        return generate_meta_tags(
            title="Availability",
            description="Your availability.",
            website_url=self.request.build_absolute_uri(
                reverse("external_availability", args=[token])
            ),
        )


class EditAvailabilityEvent(DisplayModeView):
    template_name = "diary/edit_availability_event.html"

    def get(self, request: HttpRequest, token: str):
        self.event = get_object_or_404(
            AvailabilityEvent, token=token, availability__user=request.user
        )

        display_mode = DISPLAY_MODE_SINGLE
        user_timezone = self._get_user_timezone()
        start_date = self.event.availability.date.replace(day=1)
        end_date = self._get_last_day_of_month(self.event.availability.date)

        context = {
            "today": datetime.now(tz=user_timezone).date(),
            "days": self._generate_calendar_days(
                start_date, end_date, self.event.availability.section, user_timezone
            ),
            "display_mode": display_mode,
            "event": self.event,
            "section": self.event.availability.section,
            "user_time_zone": user_timezone,
            "half_hour_intervals": half_hour_intervals,
            "reminder_options": EventReminderType.choices,
            "meta_tags": self._generate_meta_tags(token),
        }

        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, token: str):
        form = EditAvailabilityEventForm(
            {
                "token": token,
                **json.loads(request.body),
            },
            user=request.user,
        )

        if not form.is_valid():
            return ApiFormErrorResponse(form)

        event = form.save()

        return ApiSuccessKwargsResponse(
            message="Availability event updated successfully.",
            redirect=event.availability.section.token,
        )

    def _extend_day(self, current_date: date, **kwargs: typing.Any) -> dict:
        return {
            "is_selected": current_date == self.event.availability.date,
        }

    def _generate_meta_tags(self, token: str):
        return generate_meta_tags(
            title="Edit Availability Event",
            description="Edit an availability event.",
            website_url=self.request.build_absolute_uri(
                reverse("edit_availability_event", args=[token])
            ),
        )


class DeleteAvailabilityEvent(View):
    def post(self, request: HttpRequest, token: str):
        availability_event = AvailabilityEvent.objects.filter(
            token=token, availability__user=request.user
        ).first()

        section = availability_event.availability.section

        if availability_event is None:
            return ApiErrorKwargsResponse(
                message="Availability event not found.", token=token
            )

        availability_event.delete()

        return ApiSuccessKwargsResponse(
            message="Availability event deleted successfully.",
            redirect=section.token,
        )


class AddAvailabilityTimeSlot(View):
    def post(self, request: str, date: date):
        form = AddAvailabilityTimeSlotForm(
            {
                "date": date,
                **json.loads(request.body),
            },
            user=request.user,
        )

        if not form.is_valid():
            return ApiFormErrorResponse(form)

        slot = form.save()

        return ApiSuccessKwargsResponse(
            message="Availability time slot added successfully.",
            slot={
                "token": slot.token,
                "start": slot.start_time.strftime("%H:%M"),
                "end": slot.end_time.strftime("%H:%M"),
            },
        )


class RemoveAvailabilityTimeSlot(View):
    def post(self, request: HttpRequest, token: str):
        availability_time_slot = AvailabilityTimeSlot.objects.filter(
            token=token, availability__user=request.user
        ).first()

        if availability_time_slot is None:
            return ApiErrorKwargsResponse(
                message="Availability time slot not found.", token=token
            )

        availability = availability_time_slot.availability
        availability_time_slot.delete()

        if availability.time_slots.count() < 1:
            availability.delete()

        return ApiSuccessKwargsResponse(
            message="Availability time slot deleted successfully."
        )


class ClearAvailabilityTimeSlots(View):
    def post(self, request: HttpRequest, token: str):
        availability = Availability.objects.filter(
            token=token, user=request.user
        ).first()

        if availability is None:
            return ApiErrorKwargsResponse(message="Availability not found.")

        availability.time_slots.all().delete()
        availability.delete()

        return ApiSuccessKwargsResponse(message="Availability cleared successfully.")


class RenameSection(View):
    def post(self, request: HttpRequest, token: str):
        section = Section.objects.filter(token=token, user=request.user).first()

        if section is None:
            return ApiErrorKwargsResponse(message="Section not found.", token=token)

        name = json.loads(request.body).get("name", None)

        if not name:
            return ApiErrorKwargsResponse(message="Name is required.", token=token)

        section.name = name
        section.save()

        return ApiSuccessKwargsResponse(
            message="Section renamed successfully.", token=section.token
        )
