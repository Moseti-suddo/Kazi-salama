from django import forms
from .models import CareerProfile, Education


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