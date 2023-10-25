"""
Holds the views for rooms.

- RoomsListCreateView
- RoomView
- RoomAdminUpdateView
- RoomMembersCreateView
- RoomMembersDestroyView
"""

from rest_framework.generics import (
    ListCreateAPIView,
    CreateAPIView,
    UpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    DestroyAPIView,
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.core.paginator import Paginator
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from tasks.filters import TaskFilter
from .models import Room, RoomMember
from tasks.models import Task
from .serializers import *
import json

User = get_user_model()


class RoomsListCreateView(ListCreateAPIView):
    """
    View for getting room members and adding new ones.
    """

    queryset = Room.objects.all()
    serializer_class = RoomsListSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        serializer = RoomSerializer(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():
            room = serializer.save()
            return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        user = request.user.id
        user_room_memberships = RoomMember.objects.filter(
            room_member=User.objects.get(pk=user)
        )

        room_ids = [user_room.room_id for user_room in user_room_memberships]
        queryset = self.get_queryset().filter(room_id__in=room_ids)
        serializer = RoomsListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RoomView(RetrieveUpdateDestroyAPIView):
    """
    View for getting the room data, update, and deleting it.
    """

    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    filter_backends = [DjangoFilterBackend]  # Use DjangoFilterBackend for filtering
    filterset_class = TaskFilter  # Use the TaskFilter you defined

    def get_object(self):
        room_id = int(self.kwargs.get("room_id"))

        try:
            queryset = self.get_queryset().filter(room_id=room_id)
            instance = queryset.get()

            return instance

        except Room.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance is None:
            return Response(
                data="Room does not exists.",
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(instance, many=False)

        # Get the filtered tasks using django-filter
        filtered_tasks = TaskFilter(
            request.GET,
            queryset=Task.objects.filter(room=instance).order_by("-task_id"),
        ).qs

        # Paginate the filtered tasks
        paginator = Paginator(filtered_tasks, self.pagination_class.page_size)

        # Calculate the total number of pages
        total_pages = paginator.num_pages

        page = self.paginate_queryset(
            filtered_tasks.order_by("is_completed", "-task_id")
        )

        tasks_serialized = (
            [TasksListSerializer(task).data for task in page]
            if page is not None
            else []
        )

        response_data = {
            "room_data": serializer.data,
            "tasks": tasks_serialized,
            "total_pages": total_pages,
        }

        return (
            self.get_paginated_response(response_data)
            if page is not None
            else Response(response_data, status=status.HTTP_200_OK)
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(
            instance=instance,
            data=request.data,
            context={"request": request},
        )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Room.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class RoomAdminUpdateView(UpdateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomAdminUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        room_id = int(self.kwargs.get("room_id"))

        try:
            queryset = self.get_queryset().filter(room_id=room_id)
            instance = queryset.get()

            return instance

        except Room.DoesNotExist:
            raise Exception("Room does not exists.")

    def patch(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.serializer_class(
                instance=instance,
                data=request.data,
                partial=True,
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    data={"message": "Room admin updated."},
                    status=status.HTTP_200_OK,
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Room.DoesNotExist:
            return Response(
                "Room does not exist or room is invalid.",
                status=status.HTTP_404_NOT_FOUND,
            )


class RoomMembersListCreateView(ListCreateAPIView):
    """
    View for getting room members and adding new ones.
    """

    queryset = RoomMember.objects.all()
    serializer_class = RoomMembersListSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, room_id, room_slug):
        try:
            queryset = RoomMember.objects.filter(room_id=int(room_id))
        except RoomMember.DoesNotExist:
            return Response(
                data={message: "Room members does not exists."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(queryset, many=True)

        return Response({"room_members": serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, room_id, room_slug):
        try:
            queryset = Room.objects.get(room_id=int(room_id))
        except Room.DoesNotExist:
            return Response(
                data={message: "Room Does Not Exist"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = RoomMembersCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                data=RoomSerializer(queryset).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomMembersDestroyView(DestroyAPIView):
    queryset = RoomMember.objects.all()
    serializer_class = RoomMembersListSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        room_id = int(self.kwargs.get("room_id"))
        member_id = int(self.kwargs.get("member_id"))

        try:
            queryset = (
                self.get_queryset().filter(room=room_id).filter(room_member=member_id)
            )
            instance = queryset.get()
            return instance

        except RoomMember.DoesNotExist:
            raise Exception("Room Member does not exists.")

    def destroy(self, request, *args, **kwargs):
        try:
            # Get the object instance
            instance = self.get_object()

            # Update the tasker to None
            update_tasker = (
                Task.objects.filter(tasker=instance.room_member)
                .filter(room=instance.room)
                .update(tasker=None)
            )

            # Update the creator to None
            creator = (
                Task.objects.filter(creator=instance.room_member)
                .filter(room=instance.room)
                .update(creator=None)
            )

            # Delete instance and return a 204 response
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except RoomMember.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
