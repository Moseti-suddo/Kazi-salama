from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.forms import AccountEmailForm

from .forms import (
    AdvertForm,
    CareerProfileForm,
    EducationForm,
    ExperienceForm,
    SkillForm,
)
from .matching import match_skills, _found
from .models import Advert, CareerProfile, Education, Experience, Skill
from .scam import screen_advert


def get_profile(user):
    profile, _ = CareerProfile.objects.get_or_create(
        user=user,
        defaults={"full_name": user.get_full_name()},
    )
    return profile


@login_required
def profile_edit(request):
    profile = get_profile(request.user)
    was_confirmed = profile.profile_confirmed
    old_email = request.user.email

    if request.method == "POST":
        form = CareerProfileForm(request.POST, instance=profile)
        email_form = AccountEmailForm(request.POST, instance=request.user)
        profile_ok = form.is_valid()
        email_ok = email_form.is_valid()
        if profile_ok and email_ok:
            changed = (
                form.has_changed()
                or email_form.cleaned_data["email"] != old_email
            )
            with transaction.atomic():
                profile = form.save(commit=False)
                if changed:
                    profile.profile_confirmed = False
                profile.save()
                email_form.save()
            if changed and was_confirmed:
                messages.warning(
                    request,
                    "Profile saved. Your details changed, so please confirm them again.",
                )
            else:
                messages.success(request, "Profile saved.")
            return redirect("profile_edit")
    else:
        form = CareerProfileForm(instance=profile)
        email_form = AccountEmailForm(instance=request.user)

    return render(
        request,
        "profiles/profile_edit.html",
        {"form": form, "email_form": email_form, "profile": profile},
    )


@login_required
@require_POST
def profile_confirm(request):
    profile = get_profile(request.user)
    if not profile.profile_confirmed and not (profile.full_name and request.user.email):
        messages.error(
            request,
            "Add your full name and email before confirming your details.",
        )
        return redirect("profile_edit")
    profile.profile_confirmed = not profile.profile_confirmed
    profile.save(update_fields=["profile_confirmed", "updated_at"])
    return redirect("profile_edit")


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
            messages.success(request, "Education added.")
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
    if entry.is_confirmed:
        messages.success(request, "Education entry confirmed.")
    else:
        messages.info(request, "Education entry marked unconfirmed.")
    return redirect("education_list")


@login_required
def education_edit(request, pk):
    entry = get_object_or_404(Education, pk=pk, profile__user=request.user)
    was_confirmed = entry.is_confirmed

    if request.method == "POST":
        form = EducationForm(request.POST, instance=entry)
        if form.is_valid():
            changed = form.has_changed()
            entry = form.save(commit=False)
            if changed:
                entry.is_confirmed = False
            entry.save()
            if changed and was_confirmed:
                messages.warning(
                    request,
                    "Education updated. It changed, so please confirm it again.",
                )
            else:
                messages.success(request, "Education updated.")
            return redirect("education_list")
    else:
        form = EducationForm(instance=entry)

    return render(
        request,
        "profiles/education_edit.html",
        {"form": form, "entry": entry},
    )


@login_required
@require_POST
def education_delete(request, pk):
    entry = get_object_or_404(Education, pk=pk, profile__user=request.user)
    entry.delete()
    messages.success(request, "Education entry removed.")
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

    adverts = profile.adverts.all()
    cards.append({
        "name": "Adverts",
        "total": adverts.count(),
        "high_risk": adverts.filter(risk_level="High").count(),
        "url_name": "advert_list",
        "is_advert": True,
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


def _run_match(advert):
    names = advert.profile.skills.filter(is_confirmed=True).values_list("name", flat=True)
    result = match_skills(advert.text, names)
    advert.matched = result["matched"]
    advert.missing = result["missing"]
    advert.match_score = result["score"]


@login_required
def advert_list(request):
    profile = get_profile(request.user)
    if request.method == "POST":
        form = AdvertForm(request.POST)
        if form.is_valid():
            advert = form.save(commit=False)
            advert.profile = profile
            risk = screen_advert(advert.text)
            advert.risk_level = risk["level"]
            advert.risk_score = risk["score"]
            advert.indicators = risk["indicators"]
            if risk["level"] != "High":
                _run_match(advert)
            advert.save()
            return redirect("advert_detail", pk=advert.pk)
    else:
        form = AdvertForm()
    return render(
        request,
        "profiles/advert_list.html",
        {"adverts": Advert.objects.filter(profile=profile), "form": form},
    )


@login_required
def advert_detail(request, pk):
    advert = get_object_or_404(Advert, pk=pk, profile__user=request.user)
    return render(
        request,
        "profiles/advert_detail.html",
        {"advert": advert, "statuses": Advert.Status.choices},
    )


@login_required
@require_POST
def advert_override(request, pk):
    advert = get_object_or_404(Advert, pk=pk, profile__user=request.user)
    _run_match(advert)
    advert.save()
    return redirect("advert_detail", pk=pk)


@login_required
@require_POST
def advert_status(request, pk):
    advert = get_object_or_404(Advert, pk=pk, profile__user=request.user)
    new = request.POST.get("status")
    if new in Advert.Status.values:
        advert.status = new
        advert.save(update_fields=["status", "updated_at"])
    return redirect("advert_detail", pk=pk)


@login_required
@require_POST
def advert_delete(request, pk):
    advert = get_object_or_404(Advert, pk=pk, profile__user=request.user)
    advert.delete()
    return redirect("advert_list")

def _relevance(text, keywords):
    return sum(1 for k in keywords if _found(k, text))


@login_required
def advert_resume(request, pk):
    advert = get_object_or_404(Advert, pk=pk, profile__user=request.user)
    if advert.match_score is None:
        return redirect("advert_detail", pk=pk)

    profile = advert.profile
    confirmed_skills = list(profile.skills.filter(is_confirmed=True))
    result = match_skills(advert.text, [s.name for s in confirmed_skills])
    keywords = result["matched"]

    skills = sorted(confirmed_skills, key=lambda s: (s.name.lower() not in keywords, s.name.lower()))
    experience = sorted(
        profile.experience_entries.filter(is_confirmed=True).order_by("-start_date"),
        key=lambda e: -_relevance(f"{e.technologies} {e.responsibilities}", keywords),
    )
    projects = sorted(
        profile.project_entries.filter(is_confirmed=True),
        key=lambda p: -_relevance(f"{p.technologies} {p.description}", keywords),
    )
    education = profile.education_entries.filter(is_confirmed=True)

    return render(request, "profiles/resume.html", {
        "advert": advert,
        "profile": profile,
        "email": request.user.email,
        "skills": skills,
        "experience": experience,
        "projects": projects,
        "education": education,
        "keywords": keywords,
        "has_content": bool(skills or experience or projects or education),
    })