import re
from django import forms
from .models import Advert, CareerProfile, Education, Experience, Skill

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
        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

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
            "location",
            "start_date",
            "end_date",
            "is_current",
            "responsibilities",
            "technologies",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "responsibilities": forms.Textarea(attrs={"rows": 4}),
        }

class AdvertForm(forms.ModelForm):
    class Meta:
        model = Advert
        fields = ["title", "company", "source_url", "text", "deadline"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 10}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }