import datetime
import typing

import pytz

from _config.celery import app
from diary.models import AvailabilityEvent, Event, EventInvitation, EventReminderType
from utilities.tasks import send_user_notification
from utilities.time import timezone_choices


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60.0, check_reminders.s())


type_to_relative_time = {
    EventReminderType.MINUTE_BEFORE: "1 minute",
    EventReminderType._15_MINUTES_BEFORE: "15 minutes",
    EventReminderType._30_MINUTES_BEFORE: "30 minutes",
    EventReminderType.HOUR_BEFORE: "1 hour",
    EventReminderType._6_HOURS_BEFORE: "6 hours",
    EventReminderType._12_HOURS_BEFORE: "12 hours",
    EventReminderType.DAY_BEFORE: "24 hours",
    EventReminderType.WEEK_BEFORE: "7 days",
}


def append_for_datetime(
    dt: datetime.datetime,
    typ: EventReminderType,
    reminders: typing.List[
        typing.Tuple[
            typing.Union[Event, EventInvitation, AvailabilityEvent],
            str,
        ],
    ],
    timezone: str,
):
    for event in Event.objects.filter(
        dates__contains=[dt.date()],
        starting_time=dt.time().replace(second=0, microsecond=0),
        reminders__contains=[typ],
        owner__settings__time_zone=timezone,
    ):
        reminders.append((event, f"{type_to_relative_time[typ]}"))

    for invitation in EventInvitation.objects.filter(
        event__dates__contains=[dt.date()],
        event__starting_time=dt.time().replace(second=0, microsecond=0),
        event__owner__settings__time_zone=timezone,
        reminders__contains=[typ],
        accepted=True,
    ):
        reminders.append((invitation, f"{type_to_relative_time[typ]}"))

    for availability_event in AvailabilityEvent.objects.filter(
        availability__date=dt.date(),
        availability__user__settings__time_zone=timezone,
        start_time=dt.time().replace(second=0, microsecond=0),
        reminders__contains=[typ],
    ):
        reminders.append((availability_event, f"{type_to_relative_time[typ]}"))


@app.task
def check_reminders():
    for timezone in timezone_choices:
        now = datetime.datetime.now(tz=pytz.timezone(timezone[0]))

        time_in_one_minute = now + datetime.timedelta(minutes=1)
        time_in_15_minutes = now + datetime.timedelta(minutes=15)
        time_in_30_minutes = now + datetime.timedelta(minutes=30)
        time_in_1_hour = now + datetime.timedelta(hours=1)
        time_in_6_hours = now + datetime.timedelta(hours=6)
        time_in_12_hours = now + datetime.timedelta(hours=12)
        time_in_24_hours = now + datetime.timedelta(hours=24)
        time_in_7_days = now + datetime.timedelta(days=7)

        reminders: typing.List[
            typing.Tuple[
                typing.Union[Event, EventInvitation, AvailabilityEvent],
                str,
            ],
        ] = []

        append_for_datetime(
            time_in_one_minute, EventReminderType.MINUTE_BEFORE, reminders, timezone[0]
        )
        append_for_datetime(
            time_in_15_minutes,
            EventReminderType._15_MINUTES_BEFORE,
            reminders,
            timezone,
        )
        append_for_datetime(
            time_in_30_minutes,
            EventReminderType._30_MINUTES_BEFORE,
            reminders,
            timezone,
        )
        append_for_datetime(
            time_in_1_hour, EventReminderType.HOUR_BEFORE, reminders, timezone[0]
        )
        append_for_datetime(
            time_in_6_hours, EventReminderType._6_HOURS_BEFORE, reminders, timezone[0]
        )
        append_for_datetime(
            time_in_12_hours, EventReminderType._12_HOURS_BEFORE, reminders, timezone[0]
        )
        append_for_datetime(
            time_in_24_hours, EventReminderType.DAY_BEFORE, reminders, timezone[0]
        )
        append_for_datetime(
            time_in_7_days, EventReminderType.WEEK_BEFORE, reminders, timezone[0]
        )

        for reminder in reminders:
            obj, relative_time = reminder
            email = None

            context = {
                "upcoming_time": relative_time,
            }

            if isinstance(obj, Event):
                email = obj.user.email
                context.update(
                    {
                        "event_title": obj.title,
                        "event_starting_time": obj.starting_time,
                        "event_ending_time": obj.ending_time,
                        "event_dates": obj.stringify_dates(", "),
                    }
                )
            elif isinstance(obj, EventInvitation):
                email = obj.user.email
                context.update(
                    {
                        "event_title": obj.event.title,
                        "event_starting_time": obj.event.starting_time,
                        "event_ending_time": obj.event.ending_time,
                        "event_dates": obj.event.stringify_dates(", "),
                    }
                )
            elif isinstance(obj, AvailabilityEvent):
                email = obj.availability.user.email
                context.update(
                    {
                        "event_title": obj.title,
                        "event_description": obj.description,
                        "event_starting_time": obj.start_time,
                        "event_ending_time": obj.end_time,
                        "event_dates": obj.availability.date.strftime("%Y-%m-%d"),
                    }
                )

            send_user_notification.delay(
                context,
                "Upcoming event",
                "diary/email/upcoming_event.html",
                [email],
            )
