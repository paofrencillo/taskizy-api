from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UsersListView, UserRetrieveUpdateDestroyView, LogoutView


urlpatterns = [
    path("get-users/<int:room_id>/", UsersListView.as_view(), name="get-room-users"),
    path("get-users/me/", UserRetrieveUpdateDestroyView.as_view(), name="me-profile"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", LogoutView.as_view(), name="token-refresh"),
]
