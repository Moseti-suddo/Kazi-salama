from django.contrib import admin

from .models import (
    Achievement,
    CareerProfile,
    Certification,
    Education,
    Experience,
    Project,
    Skill,
)


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


# Admin bypasses the form rules (date ranges, duplicate skills) and does not
# reset is_confirmed when an entry changes. Use it to inspect and fix data.
@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("qualification", "institution", "profile", "end_date", "is_confirmed")
    list_filter = ("is_confirmed",)
    search_fields = ("qualification", "institution", "field_of_study")


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("role", "organisation", "profile", "is_current", "is_confirmed")
    list_filter = ("is_confirmed", "is_current")
    search_fields = ("role", "organisation")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "profile", "is_current", "is_confirmed")
    list_filter = ("is_confirmed", "is_current")
    search_fields = ("name", "technologies")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "profile", "is_confirmed")
    list_filter = ("is_confirmed", "category")
    search_fields = ("name",)
    filter_horizontal = ("supporting_education", "supporting_experience", "supporting_projects")


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "profile", "issue_date", "expiry_date", "is_confirmed")
    list_filter = ("is_confirmed",)
    search_fields = ("name", "provider")


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "issuer", "profile", "date", "is_confirmed")
    list_filter = ("is_confirmed",)
    search_fields = ("title", "issuer")
