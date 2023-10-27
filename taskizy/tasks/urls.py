from django.urls import path
from .views import *

urlpatterns = [
    path(
        "task/room/<int:room_id>/create/",
        TasksListCreateView.as_view(),
        name="task-create",
    ),
    path(
        "task/room/<int:room_id>/task/<int:task_id>/mark-done/",
        TaskRetrieveUpdateDestroyView.as_view(),
        name="task-complete",
    ),
    path(
        "task/room/<int:room_id>/task/<int:task_id>/delete/",
        TaskRetrieveUpdateDestroyView.as_view(),
        name="task-delete",
    ),
    path(
        "tasks/user/<int:pk>/",
        UserTasksListCreateView.as_view(),
        name="user-tasks",
    ),
]
