from django.contrib import admin
from .models import CareerProfile


@admin.register(CareerProfile)
class CareerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "location",
        "profile_confirmed",
        "updated_at",
    )
    list_filter = ("profile_confirmed",)
    search_fields = ("full_name", "location")

