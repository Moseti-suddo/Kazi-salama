from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CareerProfileForm, EducationForm
from .models import CareerProfile, Education


@login_required
def profile_edit(request):
    profile, created = CareerProfile.objects.get_or_create(
        user=request.user,
        defaults={"full_name": request.user.get_full_name()},
    )

    if request.method == "POST":
        form = CareerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile_edit")
    else:
        form = CareerProfileForm(instance=profile)

    return render(
        request,
        "profiles/profile_edit.html",
        {"form": form},
    )


@login_required
def education_list(request):
    profile = CareerProfile.objects.filter(user=request.user).first()
    education_entries = Education.objects.filter(profile=profile) if profile else []

    if request.method == "POST":
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.profile = profile
            education.save()
            return redirect("education_list")
    else:
        form = EducationForm()

    return render(
        request,
        "profiles/education_list.html",
        {
            "education_entries": education_entries,
            "form": form,
        },
    )