from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import CareerProfile
from .matching import match_skills
from .scam import screen_advert


class ScamScreeningTests(TestCase):
    def test_high_risk(self):
        text = (
            "URGENT! Guaranteed job in Dubai, no interview. Pay a KES 5,000 "
            "registration fee and send your ID copy to jobs@gmail.com or WhatsApp us only."
        )
        result = screen_advert(text)
        self.assertEqual(result["level"], "High")
        self.assertIn("Asks for a fee or deposit", result["indicators"])

    def test_medium_risk(self):
        result = screen_advert("Pay a registration fee to secure your slot. Apply now.")
        self.assertEqual(result["level"], "Medium")

    def test_low_risk(self):
        text = "We are hiring a Python developer in Nairobi. Apply through our careers page."
        result = screen_advert(text)
        self.assertEqual(result["level"], "Low")
        self.assertEqual(result["indicators"], [])


class MatchingTests(TestCase):
    def test_only_confirmed_skills_count(self):
        result = match_skills("Looking for Python, Django and SQL skills", ["Python", "SQL"])
        self.assertEqual(result["matched"], ["python", "sql"])
        self.assertEqual(result["missing"], ["django"])
        self.assertEqual(result["score"], 67)

    def test_no_required_skills(self):
        result = match_skills("A friendly team player wanted", [])
        self.assertEqual(result["score"], 0)

PASSWORD = "Kazi-Salama-2026!"


class ProfilePageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("amina", "amina@example.com", PASSWORD)
        self.client.force_login(self.user)
        self.url = reverse("profile_edit")
        self.confirm_url = reverse("profile_confirm")

    def valid_data(self, **overrides):
        data = {
            "full_name": "Amina Otieno",
            "email": "amina@example.com",
            "phone_number": "+254 712 345 678",
            "location": "Nairobi",
            "professional_summary": "Graduate developer.",
            "portfolio_url": "https://linkedin.com/in/amina",
        }
        data.update(overrides)
        return data

    def make_profile(self, **overrides):
        fields = {k: v for k, v in self.valid_data().items() if k != "email"}
        fields.update(overrides)
        return CareerProfile.objects.create(user=self.user, **fields)

    def profile(self):
        return CareerProfile.objects.get(user=self.user)

    # --- access and creation ---

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_first_visit_creates_profile_once(self):
        self.assertFalse(CareerProfile.objects.filter(user=self.user).exists())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "amina@example.com")
        self.client.get(self.url)
        self.assertEqual(CareerProfile.objects.filter(user=self.user).count(), 1)
        self.assertEqual(self.profile().full_name, "")

    # --- saving and validation ---

    def test_save_valid_profile(self):
        response = self.client.post(self.url, self.valid_data(), follow=True)
        self.assertRedirects(response, self.url)
        self.assertContains(response, "Profile saved.")
        profile = self.profile()
        self.assertEqual(profile.full_name, "Amina Otieno")
        self.assertEqual(profile.location, "Nairobi")
        self.assertFalse(profile.profile_confirmed)

    def test_full_name_required(self):
        for value in ["", "   "]:
            response = self.client.post(self.url, self.valid_data(full_name=value))
            self.assertEqual(response.status_code, 200)
            self.assertFormError(response.context["form"], "full_name", "This field is required.")
        self.assertEqual(self.profile().full_name, "")

    def test_invalid_url_rejected(self):
        response = self.client.post(self.url, self.valid_data(portfolio_url="not a url"))
        self.assertFormError(response.context["form"], "portfolio_url", "Enter a valid URL.")

    def test_url_without_scheme_gets_https(self):
        self.client.post(self.url, self.valid_data(portfolio_url="linkedin.com/in/amina"))
        self.assertEqual(self.profile().portfolio_url, "https://linkedin.com/in/amina")

    def test_invalid_phone_rejected(self):
        response = self.client.post(self.url, self.valid_data(phone_number="abc"))
        self.assertFormError(
            response.context["form"], "phone_number",
            "Use only digits, spaces, +, - and brackets.",
        )
        response = self.client.post(self.url, self.valid_data(phone_number="12-34"))
        self.assertFormError(response.context["form"], "phone_number", "Enter at least 7 digits.")

    # --- email ---

    def test_email_required_and_nothing_saved(self):
        response = self.client.post(self.url, self.valid_data(email=""))
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["email_form"], "email", "This field is required.")
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "amina@example.com")
        self.assertEqual(self.profile().full_name, "")

    def test_email_lowercased(self):
        self.client.post(self.url, self.valid_data(email="New@Example.com"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new@example.com")

    def test_duplicate_email_rejected_ignoring_case(self):
        User.objects.create_user("bob", "bob@example.com", PASSWORD)
        response = self.client.post(self.url, self.valid_data(email="BOB@example.com"))
        self.assertFormError(
            response.context["email_form"], "email",
            "An account with this email already exists.",
        )

    # --- confirmation reset on edit ---

    def test_edit_resets_confirmation(self):
        self.make_profile(profile_confirmed=True)
        response = self.client.post(self.url, self.valid_data(location="Mombasa"), follow=True)
        self.assertFalse(self.profile().profile_confirmed)
        self.assertContains(response, "please confirm them again")

    def test_unchanged_save_keeps_confirmation(self):
        self.make_profile(profile_confirmed=True)
        response = self.client.post(
            self.url, self.valid_data(email="AMINA@Example.com"), follow=True
        )
        self.assertTrue(self.profile().profile_confirmed)
        self.assertContains(response, "Profile saved.")

    # --- confirm toggle ---

    def test_confirm_requires_post(self):
        response = self.client.get(self.confirm_url)
        self.assertEqual(response.status_code, 405)

    def test_confirm_toggles(self):
        self.make_profile()
        self.client.post(self.confirm_url)
        self.assertTrue(self.profile().profile_confirmed)
        self.client.post(self.confirm_url)
        self.assertFalse(self.profile().profile_confirmed)

    def test_confirm_blocked_without_full_name(self):
        self.make_profile(full_name="")
        response = self.client.post(self.confirm_url, follow=True)
        self.assertFalse(self.profile().profile_confirmed)
        self.assertContains(response, "Add your full name and email")

    def test_confirm_blocked_without_email(self):
        self.user.email = ""
        self.user.save()
        self.make_profile()
        self.client.post(self.confirm_url)
        self.assertFalse(self.profile().profile_confirmed)

    def test_confirm_only_affects_own_profile(self):
        other = User.objects.create_user("bob", "bob@example.com", PASSWORD)
        other_profile = CareerProfile.objects.create(user=other, full_name="Bob")
        self.make_profile()
        self.client.post(self.confirm_url)
        other_profile.refresh_from_db()
        self.assertFalse(other_profile.profile_confirmed)
        self.assertTrue(self.profile().profile_confirmed)