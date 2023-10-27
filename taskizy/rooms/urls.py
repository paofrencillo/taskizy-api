from django.urls import path
from .views import (
    RoomsListCreateView,
    RoomView,
    RoomMembersListCreateView,
    RoomAdminUpdateView,
    RoomMembersDestroyView,
)

urlpatterns = [
    path(
        "rooms/",
        RoomsListCreateView.as_view(),
        name="rooms",
    ),
    path(
        "room/<int:room_id>/<slug:room_slug>/",
        RoomView.as_view(),
        name="room",
    ),
    path(
        "room/<int:room_id>/<slug:room_slug>/members/",
        RoomMembersListCreateView.as_view(),
        name="room-members",
    ),
    path(
        "room/<int:room_id>/<slug:room_slug>/assign_as_admin/",
        RoomAdminUpdateView.as_view(),
        name="room-assign-admin",
    ),
    path(
        "room/<int:room_id>/member/<int:member_id>/destroy/",
        RoomMembersDestroyView.as_view(),
        name="room-member-destroy",
    ),
]
