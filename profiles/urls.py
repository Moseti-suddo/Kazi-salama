
from django.urls import path
from .views import education_list, profile_edit


urlpatterns = [
    path("profile/", profile_edit, name="profile_edit"),
    path("profile/education/", education_list, name="education_list"),
]