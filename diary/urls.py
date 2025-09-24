from django.urls import path, register_converter

from . import views, converters

register_converter(converters.DateConverter, "date")

urlpatterns = [
    # fmt: off
    path('', views.Home.as_view(), name="home"),
    
    path('events/create', views.CreateEvent.as_view(), name="create_event"),
    path('events/<str:token>', views.EventDetails.as_view(), name="event_details"),
    path('events/<str:token>/edit', views.EditEvent.as_view(), name="edit_event"),
    path('events/<str:token>/delete', views.DeleteEvent.as_view(), name="delete_event"),
    path('events/<str:token>/guests/<str:email>/remove', views.RemoveAnonymousGuest.as_view(), name="remove_anonymous_guest"),
    
    path('invitations/view', views.Invitations.as_view(), name="view_invitations"),
    path('invitations/<str:token>/respond', views.RespondToEventInvitation.as_view(), name="respond_to_event_invitation"),
    path('invitations/<str:token>/edit', views.EditAcceptedInvitation.as_view(), name="edit_accepted_invitation"),
    path('invitations/<str:token>/remove', views.RemoveInvitation.as_view(), name="remove_invitation"),
    path('invitations/<str:token>/leave', views.LeaveInvitation.as_view(), name="leave_invitation"),

    path('availabilities/<date:date>/add', views.AddAvailabilityTimeSlot.as_view(), name="add_availability_time_slot"),
    path('availabilities/<str:token>/slots/clear', views.ClearAvailabilityTimeSlots.as_view(), name="clear_availability_time_slots"),
    path('availabilities/slots/<str:token>/remove', views.RemoveAvailabilityTimeSlot.as_view(), name="remove_availability_time_slot"),
    path('availabilities/events/<str:token>/edit', views.EditAvailabilityEvent.as_view(), name="edit_availability_event"),
    path('availabilities/events/<str:token>/delete', views.DeleteAvailabilityEvent.as_view(), name="delete_availability_event"),
    
    path('sections/add', views.AddSection.as_view(), name="add_section"),
    path('sections/<str:token>/delete', views.DeleteSection.as_view(), name="delete_section"),
    path('sections/<str:token>/rename', views.RenameSection.as_view(), name="rename_section"),
    path('sections/<str:token>/days/<date:date>', views.DayDetails.as_view(), name="day_details"),
    
    path('external/section/<str:token>', views.ExternalSectionView.as_view(), name="external_section"),
    path('external/availability/<str:token>', views.ExternalAvailability.as_view(), name="external_availability"),
        
    path('<str:section_token>', views.Home.as_view(), name="home"),
    # fmt: on
]
