from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


def clean_unique_email(email, exclude_pk=None):
    email = email.strip().lower()
    others = User.objects.filter(email__iexact=email)
    if exclude_pk is not None:
        others = others.exclude(pk=exclude_pk)
    if others.exists():
        raise forms.ValidationError("An account with this email already exists.")
    return email


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Used on your CV and for password resets.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        return clean_unique_email(self.cleaned_data["email"])


class AccountEmailForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        help_text="Shown on your CV.",
    )

    class Meta:
        model = User
        fields = ("email",)

    def clean_email(self):
        return clean_unique_email(
            self.cleaned_data["email"], exclude_pk=self.instance.pk
        )