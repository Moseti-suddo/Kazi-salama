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
        widgets = {
            "professional_summary": forms.Textarea(
                attrs={"rows": 5}
            ),
        }


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