from django.contrib import admin
from .models import Room


class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "room_name",
        "room_admin",
    )
    prepopulated_fields = {"room_slug": ("room_name",)}


admin.site.register(Room, RoomAdmin)
