from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Room, RoomMember
from tasks.models import Task
from users.serializers import UserSerializer
from tasks.serializers import TasksListSerializer
import json


User = get_user_model()


class RoomsListSerializer(serializers.ModelSerializer):
    room_admin = UserSerializer(many=False, read_only=True)
    room_members = serializers.SerializerMethodField()
    task_completed_perc = serializers.SerializerMethodField()
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            "room_id",
            "room_name",
            "room_created_on",
            "room_admin",
            "room_members",
            "room_slug",
            "task_completed_perc",
            "tasks_count",
        ]

    def get_room_members(self, obj):
        members = RoomMember.objects.filter(room=obj)
        member_serialized = [
            UserSerializer(User.objects.get(pk=member.room_member_id)).data
            for member in members
        ]

        return member_serialized

    def get_task_completed_perc(self, obj):
        try:
            tasks_count = Task.objects.filter(room=obj).count()
            completed_tasks_count = (
                Task.objects.filter(room=obj).filter(is_completed=True).count()
            )

            percentage = round((completed_tasks_count / tasks_count) * 100)

            return percentage
        except ZeroDivisionError:
            return 0

    def get_tasks_count(self, obj):
        try:
            tasks_count = Task.objects.filter(room=obj).count()
            return tasks_count
        except Room.DoesNotExist:
            raise serializers.ValidationError(
                "Room with the specified ID does not exist"
            )


class RoomSerializer(serializers.ModelSerializer):
    room_admin = UserSerializer(read_only=True)
    room_members = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()
    task_completed_perc = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            "room_id",
            "room_name",
            "room_admin",
            "room_members",
            "task_count",
            "task_completed_perc",
        ]

    def create(self, validated_data):
        try:
            user_id = self.context["request"].user.id

            room_admin = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with the specified ID does not exist"
            )

        room = Room.objects.create(
            room_admin=room_admin,
            **validated_data,
        )

        RoomMember.objects.create(
            room=room,
            room_member=room_admin,
        )

        return room

    def get_room_members(self, obj):
        members = RoomMember.objects.filter(room=obj)
        member_serialized = [
            UserSerializer(User.objects.get(pk=member.room_member_id)).data
            for member in members
        ]

        return member_serialized

    def get_task_count(self, obj):
        return Task.objects.filter(room=obj).count()

    def get_task_completed_perc(self, obj):
        try:
            tasks_count = Task.objects.filter(room=obj).count()
            completed_tasks_count = (
                Task.objects.filter(room=obj).filter(is_completed=True).count()
            )

            percentage = round((completed_tasks_count / tasks_count) * 100)

            return percentage
        except ZeroDivisionError:
            return 0


class RoomAdminUpdateSerializer(serializers.Serializer):
    room_admin = serializers.IntegerField()

    def update(self, instance, validated_data):
        new_admin_id = validated_data.get("room_admin")

        if new_admin_id is not None:
            try:
                # Get the new room_admin User instance
                new_admin = User.objects.get(pk=new_admin_id)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "User with the specified ID does not exists"
                )

            # Update the room_admin of the room instance
            instance.room_admin = new_admin
            instance.save()
        return instance


class RoomMembersListSerializer(serializers.ModelSerializer):
    room_member = UserSerializer(many=False, read_only=True)

    class Meta:
        model = RoomMember
        fields = ["room_member"]


class RoomMembersCreateSerializer(serializers.Serializer):
    room_id = serializers.IntegerField()
    new_members = serializers.CharField()

    def create(self, validated_data):
        room_id = validated_data["room_id"]
        new_members = validated_data["new_members"]
        room = Room.objects.get(pk=room_id)

        # Parse the JSON string into a list of dictionaries
        try:
            new_members = json.loads(new_members)
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format.'")

        # Assuming that 'new_members' is a list of dictionaries with 'value' and 'label' keys
        for member_data in new_members:
            user = User.objects.get(pk=member_data["value"])
            RoomMember.objects.create(room=room, room_member=user)

        return room
