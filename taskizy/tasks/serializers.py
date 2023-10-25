from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer
from .models import Task
from rooms.models import Room

User = get_user_model()


class TasksListSerializer(serializers.ModelSerializer):
    creator = UserSerializer(many=False, read_only=True)
    tasker = UserSerializer(many=False, read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(read_only=True)
    room = serializers.StringRelatedField(read_only=True)
    room_slug = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "task_id",
            "description",
            "is_urgent",
            "is_completed",
            "creator",
            "tasker",
            "room_id",
            "room",
            "room_slug",
        ]

    def get_room_slug(self, obj):
        return Room.objects.get(room_id=obj.room_id).room_slug


class TaskCreateSerializer(serializers.Serializer):
    description = serializers.CharField()
    tasker = serializers.CharField()
    is_urgent = serializers.CharField()

    def create(self, validated_data):
        try:
            tasker_id = int(validated_data["tasker"])
            creator_id = int(self.context["request"].user.id)
            room_id = int(self.context["room_id"])

            description = validated_data["description"]
            is_urgent = validated_data["is_urgent"]
            creator = User.objects.get(pk=creator_id)
            tasker = User.objects.get(pk=tasker_id)
            room = Room.objects.get(pk=room_id)

        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")

        except Room.DoesNotExist:
            raise serializers.ValidationError("Room does not exist")

        task = Task.objects.create(
            description=description,
            is_urgent=True if is_urgent == "on" else False,
            creator=creator,
            tasker=tasker,
            room=room,
        )

        return task
