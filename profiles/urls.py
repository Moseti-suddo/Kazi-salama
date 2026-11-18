from django.urls import path
from .views import (
    dashboard,
    education_confirm,
    education_list,
    profile_edit,
    skill_confirm,
    skill_list,
    experience_confirm,
    experience_list,
)

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("profile/", profile_edit, name="profile_edit"),
    path("profile/education/", education_list, name="education_list"),
    path("profile/education/<int:pk>/confirm/", education_confirm, name="education_confirm"),
    path("profile/skills/", skill_list, name="skill_list"),
    path("profile/skills/<int:pk>/confirm/", skill_confirm, name="skill_confirm"),
    path("profile/experience/", experience_list, name="experience_list"),
    path("profile/experience/<int:pk>/confirm/", experience_confirm, name="experience_confirm"),
]