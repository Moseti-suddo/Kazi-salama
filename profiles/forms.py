import re
from django import forms
from .models import (
    Achievement,
    Advert,
    CareerProfile,
    Certification,
    Education,
    Experience,
    Project,
    Skill,
)

def validate_date_range(form, cleaned_data, current_field=None):
    start = cleaned_data.get("start_date")
    end = cleaned_data.get("end_date")
    if start and end and end < start:
        form.add_error("end_date", "End date cannot be before the start date.")
    if current_field and cleaned_data.get(current_field) and end:
        form.add_error("end_date", "Leave the end date blank if you are still doing this.")

class CareerProfileForm(forms.ModelForm):
    class Meta:
        model = CareerProfile
        fields = [
            "full_name",
            "phone_number",
            "location",
            "professional_summary",
            "portfolio_url",
        ]
        labels = {
            "portfolio_url": "Portfolio or LinkedIn link",
        }
        help_texts = {
            "phone_number": "Optional. Digits, spaces, +, - and brackets, e.g. +254 712 345 678.",
            "portfolio_url": "Optional. e.g. https://linkedin.com/in/your-name",
        }
        widgets = {
            "professional_summary": forms.Textarea(
                attrs={"rows": 5}
            ),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_number"]
        if not phone:
            return phone
        if not re.fullmatch(r"[0-9+()\- ]+", phone):
            raise forms.ValidationError("Use only digits, spaces, +, - and brackets.")
        if sum(ch.isdigit() for ch in phone) < 7:
            raise forms.ValidationError("Enter at least 7 digits.")
        return phone


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = [
            "institution",
            "qualification",
            "field_of_study",
            "start_date",
            "end_date",
            "description",
        ]
        labels = {
            "end_date": "End date or expected completion",
            "description": "Coursework or description",
        }
        help_texts = {
            "start_date": "Optional.",
            "end_date": "Optional. Still studying? Enter your expected completion date.",
            "description": "Optional. e.g. relevant units, final-year project, honours.",
        }
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "end_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        validate_date_range(self, cleaned_data)
        return cleaned_data

class SkillForm(forms.ModelForm):
    supporting_education = forms.ModelMultipleChoiceField(
        queryset=Education.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Supporting education",
    )
    supporting_experience = forms.ModelMultipleChoiceField(
        queryset=Experience.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Supporting experience",
    )
    supporting_projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Supporting projects",
    )

    class Meta:
        model = Skill
        fields = [
            "name",
            "category",
            "proficiency",
            "supporting_education",
            "supporting_experience",
            "supporting_projects",
            "notes",
        ]
        labels = {
            "name": "Skill name",
            "proficiency": "Self-assessed proficiency",
        }
        help_texts = {
            "name": "e.g. Python, Django, Teamwork.",
            "proficiency": "Optional. Your own view of your level.",
            "notes": "Optional.",
        }
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, profile, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = profile
        self.fields["supporting_education"].queryset = profile.education_entries.all()
        self.fields["supporting_experience"].queryset = profile.experience_entries.all()
        self.fields["supporting_projects"].queryset = profile.project_entries.all()
    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        duplicates = self.profile.skills.filter(name__iexact=name)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("You already have a skill with this name.")
        return name

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = [
            "organisation",
            "role",
            "experience_type",
            "responsibilities",
            "location",
            "start_date",
            "end_date",
            "is_current",
            "technologies",
        ]
        labels = {
            "role": "Role title",
            "responsibilities": "Responsibilities and achievements",
            "location": "Location or remote status",
            "is_current": "I currently work here",
            "technologies": "Technologies or skills used",
        }
        help_texts = {
            "responsibilities": "What you did and what changed because of it.",
            "location": "Optional. e.g. Nairobi, or Remote.",
            "start_date": "Optional.",
            "end_date": "Optional. Leave blank if you still work here.",
            "technologies": "Optional. Separate with commas, e.g. Python, Django, PostgreSQL.",
        }
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "end_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "responsibilities": forms.Textarea(attrs={"rows": 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        validate_date_range(self, cleaned_data, current_field="is_current")
        return cleaned_data

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "role",
            "technologies",
            "outcomes",
            "start_date",
            "end_date",
            "is_current",
            "url",
        ]
        labels = {
            "name": "Project name",
            "role": "Your role or contribution",
            "technologies": "Technologies and tools",
            "outcomes": "Results or achievements",
            "is_current": "I'm still working on this",
            "url": "Repository, demo or project URL",
        }
        help_texts = {
            "description": "What the project does and the problem it solves.",
            "role": "e.g. Sole developer, or Backend lead in a team of four.",
            "technologies": "Separate with commas, e.g. Python, Django, PostgreSQL.",
            "outcomes": "Optional. e.g. Used by 200 students, or Won the faculty innovation prize.",
            "start_date": "Optional.",
            "end_date": "Optional. Leave blank if you are still working on it.",
            "url": "Optional. e.g. https://github.com/your-name/project",
        }
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "end_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "description": forms.Textarea(attrs={"rows": 4}),
            "outcomes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        validate_date_range(self, cleaned_data, current_field="is_current")
        return cleaned_data

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = [
            "name",
            "provider",
            "issue_date",
            "expiry_date",
            "url",
            "description",
        ]
        labels = {
            "name": "Certification or course name",
            "issue_date": "Issue or completion date",
            "url": "Verification URL",
            "description": "Description or topics",
        }
        help_texts = {
            "provider": "e.g. Coursera, Cisco, Google.",
            "expiry_date": "Optional. Leave blank if it does not expire.",
            "url": "Optional. A link where someone can verify it.",
            "description": "Optional. Topics covered.",
        }
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "expiry_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        issued = cleaned_data.get("issue_date")
        expiry = cleaned_data.get("expiry_date")
        if issued and expiry and expiry < issued:
            self.add_error("expiry_date", "Expiry date cannot be before the issue date.")
        return cleaned_data


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ["title", "issuer", "date", "description", "url"]
        labels = {
            "issuer": "Issuing organisation",
            "url": "Evidence URL",
        }
        help_texts = {
            "issuer": "Who gave you the award or recognition.",
            "description": "Optional.",
            "url": "Optional. A link to evidence, e.g. a certificate or news article.",
        }
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].required = True


class AdvertForm(forms.ModelForm):
    class Meta:
        model = Advert
        fields = ["title", "company", "source_url", "text", "deadline"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 10}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }