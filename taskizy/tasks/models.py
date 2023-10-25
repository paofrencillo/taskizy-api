from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rooms.models import Room

User = get_user_model()


class Task(models.Model):
    task_id = models.BigAutoField(
        _("task_ID"),
        primary_key=True,
        auto_created=True,
        serialize=False,
    )
    description = models.CharField(
        _("description"),
        max_length=100,
        null=False,
        blank=False,
    )
    is_urgent = models.BooleanField(
        _("is_urgent"),
        default=False,
        null=False,
        blank=False,
    )
    is_completed = models.BooleanField(
        _("is_completed"),
        default=False,
        null=False,
        blank=False,
    )
    creator = models.ForeignKey(
        User,
        verbose_name=_("creator_id"),
        related_name="creator_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
    )
    tasker = models.ForeignKey(
        User,
        verbose_name=_("tasker_id"),
        related_name="tasker_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
    )
    room = models.ForeignKey(
        Room,
        verbose_name=_("task_room_id"),
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )
