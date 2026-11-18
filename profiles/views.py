from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CareerProfileForm, EducationForm, ExperienceForm, SkillForm
from .models import CareerProfile, Education, Experience, Skill

def get_profile(user):
    profile, _ = CareerProfile.objects.get_or_create(
        user=user,
        defaults={"full_name": user.get_full_name()},
    )
    return profile


@login_required
def profile_edit(request):
    profile = get_profile(request.user)

    if request.method == "POST":
        form = CareerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile_edit")
    else:
        form = CareerProfileForm(instance=profile)

    return render(request, "profiles/profile_edit.html", {"form": form})


@login_required
def education_list(request):
    profile = get_profile(request.user)
    education_entries = Education.objects.filter(profile=profile)

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
        {"education_entries": education_entries, "form": form},
    )


@login_required
@require_POST
def education_confirm(request, pk):
    entry = get_object_or_404(Education, pk=pk, profile__user=request.user)
    entry.is_confirmed = not entry.is_confirmed
    entry.save(update_fields=["is_confirmed", "updated_at"])
    return redirect("education_list")

@login_required
def dashboard(request):
    profile = get_profile(request.user)
    sections = [
        ("Education", profile.education_entries, "education_list"),
        ("Experience", profile.experience_entries, "experience_list"),
        ("Projects", profile.project_entries, None),
        ("Skills", profile.skills, "skill_list"),
        ("Certifications", profile.certifications, None),
        ("Achievements", profile.achievements, None),
    ]
    cards = []
    for name, manager, url_name in sections:
        total = manager.count()
        confirmed = manager.filter(is_confirmed=True).count()
        cards.append({
            "name": name,
            "total": total,
            "confirmed": confirmed,
            "unconfirmed": total - confirmed,
            "url_name": url_name,
        })
    return render(request, "profiles/dashboard.html", {"profile": profile, "cards": cards})

@login_required
def skill_list(request):
    profile = get_profile(request.user)
    skills = Skill.objects.filter(profile=profile).order_by("name")

    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.profile = profile
            skill.save()
            return redirect("skill_list")
    else:
        form = SkillForm()

    return render(
        request,
        "profiles/skill_list.html",
        {"skills": skills, "form": form},
    )


@login_required
@require_POST
def skill_confirm(request, pk):
    skill = get_object_or_404(Skill, pk=pk, profile__user=request.user)
    skill.is_confirmed = not skill.is_confirmed
    skill.save(update_fields=["is_confirmed", "updated_at"])
    return redirect("skill_list")

@login_required
def experience_list(request):
    profile = get_profile(request.user)
    entries = Experience.objects.filter(profile=profile).order_by("-start_date")

    if request.method == "POST":
        form = ExperienceForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.profile = profile
            entry.save()
            return redirect("experience_list")
    else:
        form = ExperienceForm()

    return render(
        request,
        "profiles/experience_list.html",
        {"entries": entries, "form": form},
    )


@login_required
@require_POST
def experience_confirm(request, pk):
    entry = get_object_or_404(Experience, pk=pk, profile__user=request.user)
    entry.is_confirmed = not entry.is_confirmed
    entry.save(update_fields=["is_confirmed", "updated_at"])
    return redirect("experience_list")