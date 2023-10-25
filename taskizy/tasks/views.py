from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import Task
from .serializers import TasksListSerializer, TaskCreateSerializer
from .filters import TaskFilter


User = get_user_model()


class TasksListCreateView(ListCreateAPIView):
    """
    View for retrieving a task list of a room and also create ones.
    """

    queryset = Task.objects.all()
    serializer_class = TasksListSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, room_id, room_slug):
        queryset = self.get_queryset().filter(room_id=room_id)
        serializer = self.serializer_class(
            queryset,
            many=True,
        )

        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, room_id):
        serializer = TaskCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "room_id": room_id,
            },
        )

        if serializer.is_valid():
            task = serializer.save()
            return Response(
                TasksListSerializer(task).data, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserTasksListCreateView(ListCreateAPIView):
    """
    View for retrieve a list of user tasks and create task.
    """

    queryset = Task.objects.all()
    serializer_class = TasksListSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]  # Use DjangoFilterBackend for filtering
    filterset_class = TaskFilter  # Use the TaskFilter you defined

    def list(self, request, *args, **kwargs):
        try:
            user = request.user.id
            userID_from_url = self.kwargs.get("pk")

            # Check first if request.user.id == userID from the URL
            if user != userID_from_url:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            # Get the filtered tasks using django-filter
            filtered_tasks = TaskFilter(
                request.GET,
                queryset=self.get_queryset()
                .filter(tasker=User.objects.get(pk=user))
                .order_by("-task_id"),
            ).qs

            # Paginate the filtered tasks
            paginator = Paginator(filtered_tasks, self.pagination_class.page_size)

            # Calculate the total number of pages
            total_pages = paginator.num_pages

            # Query the tasks based on the filter/s
            page = self.paginate_queryset(
                filtered_tasks.order_by("is_completed", "-task_id")
            )

            # Serialize the tasks
            tasks_serialized = (
                [TasksListSerializer(task).data for task in page]
                if page is not None
                else []
            )

            # Return the response
            response_data = {
                "tasks": tasks_serialized,
                "total_pages": total_pages,
            }

            return (
                self.get_paginated_response(response_data)
                if page is not None
                else Response(response_data, status=status.HTTP_200_OK)
            )

        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        pass


class TaskRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    View for executing RUD on selected task.
    """

    queryset = Task.objects.all()
    serializer_class = TasksListSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        task_id = int(self.kwargs.get("task_id"))
        room_id = int(self.kwargs.get("room_id"))

        try:
            queryset = Task.objects.filter(task_id=task_id, room=room_id)
            instance = queryset.get()

            return instance

        except Task.DoesNotExist:
            raise Exception("Task does not exist or room is invalid.")

    def retrieve(self, request, room_id, room_slug):
        pass

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Task.DoesNotExist:
            return Response(
                "Task does not exist or room is invalid.",
                status=status.HTTP_404_NOT_FOUND,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
