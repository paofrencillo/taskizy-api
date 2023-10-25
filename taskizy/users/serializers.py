from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer


User = get_user_model()


class CreateUserSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "user_image",
        ]

    def get_user_image(self, obj):
        try:
            img = obj.user_image_url
            return img
        except ValueError:
            return None


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "user_image",
        ]

    def get_user_image(self, obj):
        try:
            img = obj.user_image_url
            return img
        except ValueError:
            return None

    # def update(self, instance, validated_data):
    #     pass


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["first_name"] = user.first_name
        token["last_name"] = user.last_name

        try:
            token["user_image"] = user.user_image.url
        except ValueError:
            token["user_image"] = None

        return token
