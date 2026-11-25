import re
from django import forms
from .models import Advert, CareerProfile, Education, Experience, Skill

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
    class Meta:
        model = Skill
        fields = ["name", "category", "proficiency", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

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


class AdvertForm(forms.ModelForm):
    class Meta:
        model = Advert
        fields = ["title", "company", "source_url", "text", "deadline"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 10}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }