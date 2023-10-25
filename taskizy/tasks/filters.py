import django_filters as df
from .models import Task


class TaskFilter(df.FilterSet):
    creator_id = df.NumberFilter(field_name="creator__id")
    tasker_id = df.NumberFilter(field_name="tasker__id")
    is_completed = df.BooleanFilter(field_name="is_completed")

    class Meta:
        model = Task
        fields = ["creator__id", "tasker__id", "is_completed"]
