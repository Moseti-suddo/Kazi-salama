
from django.db import models

from django.conf import settings


class CareerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="career_profile",
    )
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=150, blank=True)
    professional_summary = models.TextField(blank=True)
    portfolio_url = models.URLField(blank=True)
    profile_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class Education(models.Model):
    profile = models.ForeignKey(
        CareerProfile,
        on_delete=models.CASCADE,
        related_name="education_entries",
    )
    institution = models.CharField(max_length=200)
    qualification = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-end_date", "-start_date"]

    def __str__(self):
        return f"{self.qualification} — {self.institution}"


class Experience(models.Model):
    class ExperienceType(models.TextChoices):
        EMPLOYMENT = "employment", "Employment"
        INTERNSHIP = "internship", "Internship"
        VOLUNTEER = "volunteer", "Volunteer"

    profile = models.ForeignKey(
        CareerProfile,
        on_delete=models.CASCADE,
        related_name="experience_entries",
    )
    organisation = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    experience_type = models.CharField(
        max_length=20,
        choices=ExperienceType.choices,
    )
    location = models.CharField(max_length=150, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    responsibilities = models.TextField()
    technologies = models.CharField(max_length=500, blank=True)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.role} — {self.organisation}"


class Project(models.Model):
    profile = models.ForeignKey(
        CareerProfile,
        on_delete=models.CASCADE,
        related_name="project_entries",
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    role = models.CharField(max_length=200)
    technologies = models.CharField(max_length=500)
    outcomes = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    url = models.URLField(blank=True)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Skill(models.Model):
    class Category(models.TextChoices):
        LANGUAGE = "language", "Language"
        FRAMEWORK = "framework", "Framework"
        DATABASE = "database", "Database"
        TOOL = "tool", "Tool"
        SOFT_SKILL = "soft_skill", "Soft skill"

    class Proficiency(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"
        EXPERT = "expert", "Expert"

    profile = models.ForeignKey(
        CareerProfile,
        on_delete=models.CASCADE,
        related_name="skills",
    )
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=Category.choices)
    proficiency = models.CharField(
        max_length=20,
        choices=Proficiency.choices,
        blank=True,
    )
    notes = models.TextField(blank=True)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Certification(models.Model):
    profile = models.ForeignKey(
        CareerProfile,
        on_delete=models.CASCADE,
        related_name="certifications",
    )
    name = models.CharField(max_length=200)
    provider = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Achievement(models.Model):
    profile = models.ForeignKey(
        CareerProfile,
        on_delete=models.CASCADE,
        related_name="achievements",
    )
    title = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200)
    date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title