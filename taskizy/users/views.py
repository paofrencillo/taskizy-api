from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from rooms.models import RoomMember


User = get_user_model()


class UsersListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, room_id):
        try:
            member_queryset = RoomMember.objects.filter(room_id=room_id)
            user_queryset = User.objects.exclude(is_superuser=True).exclude(
                pk__in=[member.room_member_id for member in member_queryset]
            )
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            instance = self.request.user
            return instance
        except User.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance is not None:
            serializer = self.serializer_class(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data

        if instance is not None:
            serializer = self.serializer_class(
                instance=instance, data=data, partial=True
            )

            if serializer.is_valid():
                user = serializer.save()
                user_serialzed = UserSerializer(instance=user)
                return Response(
                    user_serialzed.data, status=status.HTTP_205_RESET_CONTENT
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(user_serialzed.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, requests, *args, **kwargs):
        pass


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
