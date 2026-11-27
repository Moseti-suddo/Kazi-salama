from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Achievement,
    CareerProfile,
    Certification,
    Education,
    Experience,
    Project,
    Skill,
)

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

   
class EducationPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("amina", "amina@example.com", PASSWORD)
        self.client.force_login(self.user)
        self.profile = CareerProfile.objects.create(user=self.user, full_name="Amina Otieno")
        self.url = reverse("education_list")

    def valid_data(self, **overrides):
        data = {
            "institution": "University of Nairobi",
            "qualification": "BSc",
            "field_of_study": "Computer Science",
            "start_date": "2021-09-01",
            "end_date": "2025-07-31",
            "description": "Final-year project: job-scam detector.",
        }
        data.update(overrides)
        return data

    def make_entry(self, profile=None, **overrides):
        fields = {
            "institution": "University of Nairobi",
            "qualification": "BSc",
            "field_of_study": "Computer Science",
            "start_date": date(2021, 9, 1),
            "end_date": date(2025, 7, 31),
            "description": "Final-year project: job-scam detector.",
        }
        fields.update(overrides)
        return Education.objects.create(profile=profile or self.profile, **fields)

    def other_entry(self):
        other = User.objects.create_user("bob", "bob@example.com", PASSWORD)
        other_profile = CareerProfile.objects.create(user=other, full_name="Bob")
        return self.make_entry(profile=other_profile, qualification="Diploma")

    # --- access and adding ---

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_add_entry(self):
        response = self.client.post(self.url, self.valid_data())
        self.assertRedirects(response, self.url)
        entry = Education.objects.get()
        self.assertEqual(entry.profile, self.profile)
        self.assertEqual(entry.end_date, date(2025, 7, 31))
        self.assertFalse(entry.is_confirmed)

    def test_required_fields(self):
        for field in ["institution", "qualification", "field_of_study"]:
            with self.subTest(field=field):
                response = self.client.post(self.url, self.valid_data(**{field: ""}))
                self.assertEqual(response.status_code, 200)
                self.assertFormError(response.context["form"], field, "This field is required.")
        self.assertEqual(Education.objects.count(), 0)

    def test_dates_optional(self):
        self.client.post(self.url, self.valid_data(start_date="", end_date=""))
        entry = Education.objects.get()
        self.assertIsNone(entry.start_date)
        self.assertIsNone(entry.end_date)

    # --- date rule ---

    def test_end_before_start_rejected(self):
        response = self.client.post(
            self.url, self.valid_data(start_date="2025-09-01", end_date="2021-07-31")
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "end_date", "End date cannot be before the start date."
        )
        self.assertEqual(Education.objects.count(), 0)

    def test_equal_dates_allowed(self):
        self.client.post(self.url, self.valid_data(start_date="2024-01-15", end_date="2024-01-15"))
        self.assertEqual(Education.objects.count(), 1)

    def test_future_end_date_shown_as_expected(self):
        future = timezone.localdate() + timedelta(days=365)
        self.make_entry(end_date=future)
        response = self.client.get(self.url)
        self.assertContains(response, "Expected")

    def test_past_end_date_not_shown_as_expected(self):
        self.make_entry()
        response = self.client.get(self.url)
        self.assertNotContains(response, "Expected ")

    # --- edit ---

    def test_edit_page_shows_saved_dates(self):
        entry = self.make_entry()
        response = self.client.get(reverse("education_edit", args=[entry.pk]))
        self.assertContains(response, 'value="2021-09-01"')
        self.assertContains(response, 'value="2025-07-31"')

    def test_edit_saves_changes(self):
        entry = self.make_entry()
        response = self.client.post(
            reverse("education_edit", args=[entry.pk]),
            self.valid_data(qualification="BSc (Hons)"),
        )
        self.assertRedirects(response, self.url)
        entry.refresh_from_db()
        self.assertEqual(entry.qualification, "BSc (Hons)")

    def test_edit_resets_confirmation(self):
        entry = self.make_entry(is_confirmed=True)
        response = self.client.post(
            reverse("education_edit", args=[entry.pk]),
            self.valid_data(qualification="BSc (Hons)"),
            follow=True,
        )
        entry.refresh_from_db()
        self.assertFalse(entry.is_confirmed)
        self.assertContains(response, "please confirm it again")

    def test_unchanged_save_keeps_confirmation(self):
        entry = self.make_entry(is_confirmed=True)
        self.client.post(reverse("education_edit", args=[entry.pk]), self.valid_data())
        entry.refresh_from_db()
        self.assertTrue(entry.is_confirmed)

    def test_edit_rejects_end_before_start(self):
        entry = self.make_entry()
        response = self.client.post(
            reverse("education_edit", args=[entry.pk]),
            self.valid_data(end_date="2020-01-01"),
        )
        self.assertFormError(
            response.context["form"], "end_date", "End date cannot be before the start date."
        )
        entry.refresh_from_db()
        self.assertEqual(entry.end_date, date(2025, 7, 31))

    def test_cannot_edit_other_users_entry(self):
        entry = self.other_entry()
        url = reverse("education_edit", args=[entry.pk])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(url, self.valid_data()).status_code, 404)
        entry.refresh_from_db()
        self.assertEqual(entry.qualification, "Diploma")

    # --- remove ---

    def test_delete_requires_post(self):
        entry = self.make_entry()
        response = self.client.get(reverse("education_delete", args=[entry.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Education.objects.filter(pk=entry.pk).exists())

    def test_delete_own_entry(self):
        entry = self.make_entry()
        response = self.client.post(reverse("education_delete", args=[entry.pk]))
        self.assertRedirects(response, self.url)
        self.assertFalse(Education.objects.filter(pk=entry.pk).exists())

    def test_cannot_delete_other_users_entry(self):
        entry = self.other_entry()
        response = self.client.post(reverse("education_delete", args=[entry.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Education.objects.filter(pk=entry.pk).exists())

    # --- confirm ---

    def test_confirm_toggles(self):
        entry = self.make_entry()
        url = reverse("education_confirm", args=[entry.pk])
        self.client.post(url)
        entry.refresh_from_db()
        self.assertTrue(entry.is_confirmed)
        self.client.post(url)
        entry.refresh_from_db()
        self.assertFalse(entry.is_confirmed)

    def test_cannot_confirm_other_users_entry(self):
        entry = self.other_entry()
        response = self.client.post(reverse("education_confirm", args=[entry.pk]))
        self.assertEqual(response.status_code, 404)
        entry.refresh_from_db()
        self.assertFalse(entry.is_confirmed)

    # --- ordering ---

    def test_ordering(self):
        older = self.make_entry(end_date=date(2020, 7, 1))
        newer = self.make_entry(end_date=date(2024, 7, 1))
        no_dates = self.make_entry(start_date=None, end_date=None)
        self.assertEqual(
            list(Education.objects.filter(profile=self.profile)),
            [no_dates, newer, older],
        )

class ExperiencePageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("amina", "amina@example.com", PASSWORD)
        self.client.force_login(self.user)
        self.profile = CareerProfile.objects.create(user=self.user, full_name="Amina Otieno")
        self.url = reverse("experience_list")

    def valid_data(self, **overrides):
        data = {
            "organisation": "Safaricom",
            "role": "Software Engineering Intern",
            "experience_type": "internship",
            "responsibilities": "Built internal Django dashboards.",
            "location": "Nairobi",
            "start_date": "2024-01-08",
            "end_date": "2024-06-28",
            "technologies": "Python, Django",
        }
        data.update(overrides)
        return data

    def make_entry(self, profile=None, **overrides):
        fields = {
            "organisation": "Safaricom",
            "role": "Software Engineering Intern",
            "experience_type": "internship",
            "responsibilities": "Built internal Django dashboards.",
            "location": "Nairobi",
            "start_date": date(2024, 1, 8),
            "end_date": date(2024, 6, 28),
            "technologies": "Python, Django",
        }
        fields.update(overrides)
        return Experience.objects.create(profile=profile or self.profile, **fields)

    def other_entry(self):
        other = User.objects.create_user("bob", "bob@example.com", PASSWORD)
        other_profile = CareerProfile.objects.create(user=other, full_name="Bob")
        return self.make_entry(profile=other_profile, role="Volunteer Tutor")

    # --- access and adding ---

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_add_entry(self):
        response = self.client.post(self.url, self.valid_data(), follow=True)
        self.assertRedirects(response, self.url)
        self.assertContains(response, "Experience added.")
        entry = Experience.objects.get()
        self.assertEqual(entry.profile, self.profile)
        self.assertEqual(entry.start_date, date(2024, 1, 8))
        self.assertFalse(entry.is_current)
        self.assertFalse(entry.is_confirmed)

    def test_required_fields(self):
        for field in ["organisation", "role", "experience_type", "responsibilities"]:
            with self.subTest(field=field):
                response = self.client.post(self.url, self.valid_data(**{field: ""}))
                self.assertEqual(response.status_code, 200)
                self.assertFormError(response.context["form"], field, "This field is required.")
        self.assertEqual(Experience.objects.count(), 0)

    def test_optional_fields_blank(self):
        self.client.post(
            self.url,
            self.valid_data(location="", start_date="", end_date="", technologies=""),
        )
        entry = Experience.objects.get()
        self.assertIsNone(entry.start_date)
        self.assertIsNone(entry.end_date)
        self.assertEqual(entry.location, "")

    def test_unknown_experience_type_rejected(self):
        response = self.client.post(self.url, self.valid_data(experience_type="freelance"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("experience_type", response.context["form"].errors)
        self.assertEqual(Experience.objects.count(), 0)

    # --- date rules ---

    def test_end_before_start_rejected(self):
        response = self.client.post(
            self.url, self.valid_data(start_date="2024-06-01", end_date="2024-01-01")
        )
        self.assertFormError(
            response.context["form"], "end_date", "End date cannot be before the start date."
        )
        self.assertEqual(Experience.objects.count(), 0)

    def test_equal_dates_allowed(self):
        self.client.post(self.url, self.valid_data(start_date="2024-03-01", end_date="2024-03-01"))
        self.assertEqual(Experience.objects.count(), 1)

    def test_current_with_end_date_rejected(self):
        response = self.client.post(self.url, self.valid_data(is_current="on"))
        self.assertFormError(
            response.context["form"],
            "end_date",
            "Leave the end date blank if you are still doing this.",
        )
        self.assertEqual(Experience.objects.count(), 0)

    def test_current_without_end_date_allowed(self):
        self.client.post(self.url, self.valid_data(is_current="on", end_date=""))
        entry = Experience.objects.get()
        self.assertTrue(entry.is_current)
        self.assertIsNone(entry.end_date)

    def test_current_shown_as_present(self):
        self.make_entry(is_current=True, end_date=None)
        response = self.client.get(self.url)
        self.assertContains(response, "Jan 2024")
        self.assertContains(response, "Present")

    # --- listing and ordering ---

    def test_only_own_entries_listed(self):
        self.other_entry()
        mine = self.make_entry()
        response = self.client.get(self.url)
        self.assertEqual(list(response.context["entries"]), [mine])

    def test_ordering_current_first_then_most_recent(self):
        older = self.make_entry(start_date=date(2019, 1, 1), end_date=date(2020, 1, 1))
        current = self.make_entry(start_date=date(2023, 1, 1), end_date=None, is_current=True)
        newer = self.make_entry(start_date=date(2021, 1, 1), end_date=date(2022, 12, 31))
        response = self.client.get(self.url)
        self.assertEqual(list(response.context["entries"]), [current, newer, older])

    # --- edit ---

    def test_edit_page_shows_saved_dates(self):
        entry = self.make_entry()
        response = self.client.get(reverse("experience_edit", args=[entry.pk]))
        self.assertContains(response, 'value="2024-01-08"')
        self.assertContains(response, 'value="2024-06-28"')

    def test_edit_saves_changes(self):
        entry = self.make_entry()
        response = self.client.post(
            reverse("experience_edit", args=[entry.pk]),
            self.valid_data(role="Junior Developer"),
        )
        self.assertRedirects(response, self.url)
        entry.refresh_from_db()
        self.assertEqual(entry.role, "Junior Developer")

    def test_edit_resets_confirmation(self):
        entry = self.make_entry(is_confirmed=True)
        response = self.client.post(
            reverse("experience_edit", args=[entry.pk]),
            self.valid_data(role="Junior Developer"),
            follow=True,
        )
        entry.refresh_from_db()
        self.assertFalse(entry.is_confirmed)
        self.assertContains(response, "please confirm it again")

    def test_unchanged_edit_keeps_confirmation(self):
        entry = self.make_entry(is_confirmed=True)
        self.client.post(reverse("experience_edit", args=[entry.pk]), self.valid_data())
        entry.refresh_from_db()
        self.assertTrue(entry.is_confirmed)

    def test_edit_with_bad_dates_not_saved(self):
        entry = self.make_entry()
        response = self.client.post(
            reverse("experience_edit", args=[entry.pk]),
            self.valid_data(end_date="2023-01-01"),
        )
        self.assertEqual(response.status_code, 200)
        entry.refresh_from_db()
        self.assertEqual(entry.end_date, date(2024, 6, 28))

    def test_cannot_edit_other_users_entry(self):
        entry = self.other_entry()
        response = self.client.get(reverse("experience_edit", args=[entry.pk]))
        self.assertEqual(response.status_code, 404)

    # --- remove ---

    def test_delete_removes_entry(self):
        entry = self.make_entry()
        response = self.client.post(reverse("experience_delete", args=[entry.pk]))
        self.assertRedirects(response, self.url)
        self.assertFalse(Experience.objects.filter(pk=entry.pk).exists())

    def test_delete_requires_post(self):
        entry = self.make_entry()
        response = self.client.get(reverse("experience_delete", args=[entry.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Experience.objects.filter(pk=entry.pk).exists())

    def test_cannot_delete_other_users_entry(self):
        entry = self.other_entry()
        response = self.client.post(reverse("experience_delete", args=[entry.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Experience.objects.filter(pk=entry.pk).exists())

    # --- confirm ---

    def test_confirm_toggles(self):
        entry = self.make_entry()
        url = reverse("experience_confirm", args=[entry.pk])
        self.client.post(url)
        entry.refresh_from_db()
        self.assertTrue(entry.is_confirmed)
        self.client.post(url)
        entry.refresh_from_db()
        self.assertFalse(entry.is_confirmed)

    def test_cannot_confirm_other_users_entry(self):
        entry = self.other_entry()
        response = self.client.post(reverse("experience_confirm", args=[entry.pk]))
        self.assertEqual(response.status_code, 404)
        entry.refresh_from_db()
        self.assertFalse(entry.is_confirmed)

class ProjectPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("amina", "amina@example.com", PASSWORD)
        self.client.force_login(self.user)
        self.profile = CareerProfile.objects.create(user=self.user, full_name="Amina Otieno")
        self.url = reverse("project_list")

    def valid_data(self, **overrides):
        data = {
            "name": "Kazi Salama",
            "description": "Career profile and job-advert scam screening.",
            "role": "Sole developer",
            "technologies": "Python, Django, PostgreSQL",
            "outcomes": "Presented to the project panel.",
            "start_date": "2026-01-12",
            "end_date": "2026-11-30",
            "url": "https://github.com/amina/kazi",
        }
        data.update(overrides)
        return data

    def make_entry(self, profile=None, **overrides):
        fields = {
            "name": "Kazi Salama",
            "description": "Career profile and job-advert scam screening.",
            "role": "Sole developer",
            "technologies": "Python, Django, PostgreSQL",
            "outcomes": "Presented to the project panel.",
            "start_date": date(2026, 1, 12),
            "end_date": date(2026, 11, 30),
            "url": "https://github.com/amina/kazi",
        }
        fields.update(overrides)
        return Project.objects.create(profile=profile or self.profile, **fields)

    def other_entry(self):
        other = User.objects.create_user("bob", "bob@example.com", PASSWORD)
        other_profile = CareerProfile.objects.create(user=other, full_name="Bob")
        return self.make_entry(profile=other_profile, name="Bob's project")

    # --- access and adding ---

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_add_entry(self):
        response = self.client.post(self.url, self.valid_data(), follow=True)
        self.assertRedirects(response, self.url)
        self.assertContains(response, "Project added.")
        entry = Project.objects.get()
        self.assertEqual(entry.profile, self.profile)
        self.assertEqual(entry.start_date, date(2026, 1, 12))
        self.assertFalse(entry.is_current)
        self.assertFalse(entry.is_confirmed)

    def test_required_fields(self):
        for field in ["name", "description", "role", "technologies"]:
            with self.subTest(field=field):
                response = self.client.post(self.url, self.valid_data(**{field: ""}))
                self.assertEqual(response.status_code, 200)
                self.assertFormError(response.context["form"], field, "This field is required.")
        self.assertEqual(Project.objects.count(), 0)

    def test_optional_fields_blank(self):
        self.client.post(
            self.url,
            self.valid_data(outcomes="", start_date="", end_date="", url=""),
        )
        entry = Project.objects.get()
        self.assertIsNone(entry.start_date)
        self.assertIsNone(entry.end_date)
        self.assertEqual(entry.url, "")

    def test_url_without_scheme_gets_https(self):
        self.client.post(self.url, self.valid_data(url="github.com/amina/kazi"))
        self.assertEqual(Project.objects.get().url, "https://github.com/amina/kazi")

    def test_invalid_url_rejected(self):
        response = self.client.post(self.url, self.valid_data(url="not a url"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("url", response.context["form"].errors)
        self.assertEqual(Project.objects.count(), 0)

    # --- date rules ---

    def test_end_before_start_rejected(self):
        response = self.client.post(
            self.url, self.valid_data(start_date="2026-06-01", end_date="2026-01-01")
        )
        self.assertFormError(
            response.context["form"], "end_date", "End date cannot be before the start date."
        )
        self.assertEqual(Project.objects.count(), 0)

    def test_equal_dates_allowed(self):
        self.client.post(self.url, self.valid_data(start_date="2026-03-01", end_date="2026-03-01"))
        self.assertEqual(Project.objects.count(), 1)

    def test_current_with_end_date_rejected(self):
        response = self.client.post(self.url, self.valid_data(is_current="on"))
        self.assertFormError(
            response.context["form"],
            "end_date",
            "Leave the end date blank if you are still doing this.",
        )
        self.assertEqual(Project.objects.count(), 0)

    def test_current_without_end_date_allowed(self):
        self.client.post(self.url, self.valid_data(is_current="on", end_date=""))
        entry = Project.objects.get()
        self.assertTrue(entry.is_current)
        self.assertIsNone(entry.end_date)

    def test_current_shown_as_present(self):
        self.make_entry(is_current=True, end_date=None)
        response = self.client.get(self.url)
        self.assertContains(response, "Jan 2026")
        self.assertContains(response, "Present")

    # --- listing and ordering ---

    def test_only_own_entries_listed(self):
        self.other_entry()
        mine = self.make_entry()
        response = self.client.get(self.url)
        self.assertEqual(list(response.context["entries"]), [mine])

    def test_ordering_current_first_then_most_recent(self):
        older = self.make_entry(start_date=date(2023, 1, 1), end_date=date(2023, 6, 1))
        current = self.make_entry(start_date=date(2025, 1, 1), end_date=None, is_current=True)
        newer = self.make_entry(start_date=date(2024, 1, 1), end_date=date(2024, 12, 1))
        response = self.client.get(self.url)
        self.assertEqual(list(response.context["entries"]), [current, newer, older])

    def test_dashboard_links_to_projects(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, f'href="{self.url}"')

    # --- edit ---

    def test_edit_page_shows_saved_dates(self):
        entry = self.make_entry()
        response = self.client.get(reverse("project_edit", args=[entry.pk]))
        self.assertContains(response, 'value="2026-01-12"')
        self.assertContains(response, 'value="2026-11-30"')

    def test_edit_saves_changes(self):
        entry = self.make_entry()
        response = self.client.post(
            reverse("project_edit", args=[entry.pk]),
            self.valid_data(role="Backend lead"),
        )
        self.assertRedirects(response, self.url)
        entry.refresh_from_db()
        self.assertEqual(entry.role, "Backend lead")

    def test_edit_resets_confirmation(self):
        entry = self.make_entry(is_confirmed=True)
        response = self.client.post(
            reverse("project_edit", args=[entry.pk]),
            self.valid_data(role="Backend lead"),
            follow=True,
        )
        entry.refresh_from_db()
        self.assertFalse(entry.is_confirmed)
        self.assertContains(response, "please confirm it again")

    def test_unchanged_edit_keeps_confirmation(self):
        entry = self.make_entry(is_confirmed=True)
        self.client.post(reverse("project_edit", args=[entry.pk]), self.valid_data())
        entry.refresh_from_db()
        self.assertTrue(entry.is_confirmed)

    def test_edit_with_bad_dates_not_saved(self):
        entry = self.make_entry()
        response = self.client.post(
            reverse("project_edit", args=[entry.pk]),
            self.valid_data(end_date="2025-01-01"),
        )
        self.assertEqual(response.status_code, 200)
        entry.refresh_from_db()
        self.assertEqual(entry.end_date, date(2026, 11, 30))

    def test_cannot_edit_other_users_entry(self):
        entry = self.other_entry()
        response = self.client.get(reverse("project_edit", args=[entry.pk]))
        self.assertEqual(response.status_code, 404)

    # --- remove ---

    def test_delete_removes_entry(self):
        entry = self.make_entry()
        response = self.client.post(reverse("project_delete", args=[entry.pk]))
        self.assertRedirects(response, self.url)
        self.assertFalse(Project.objects.filter(pk=entry.pk).exists())

    def test_delete_requires_post(self):
        entry = self.make_entry()
        response = self.client.get(reverse("project_delete", args=[entry.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Project.objects.filter(pk=entry.pk).exists())

    def test_cannot_delete_other_users_entry(self):
        entry = self.other_entry()
        response = self.client.post(reverse("project_delete", args=[entry.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Project.objects.filter(pk=entry.pk).exists())

    # --- confirm ---

    def test_confirm_toggles(self):
        entry = self.make_entry()
        url = reverse("project_confirm", args=[entry.pk])
        self.client.post(url)
        entry.refresh_from_db()
        self.assertTrue(entry.is_confirmed)
        self.client.post(url)
        entry.refresh_from_db()
        self.assertFalse(entry.is_confirmed)

    def test_cannot_confirm_other_users_entry(self):
        entry = self.other_entry()
        response = self.client.post(reverse("project_confirm", args=[entry.pk]))
        self.assertEqual(response.status_code, 404)
        entry.refresh_from_db()
        self.assertFalse(entry.is_confirmed)

class SkillPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("amina", "amina@example.com", PASSWORD)
        self.client.force_login(self.user)
        self.profile = CareerProfile.objects.create(user=self.user, full_name="Amina Otieno")
        self.url = reverse("skill_list")

    def valid_data(self, **overrides):
        data = {
            "name": "Python",
            "category": Skill.Category.LANGUAGE,
            "proficiency": "",
            "notes": "",
        }
        data.update(overrides)
        return data

    def make_skill(self, profile=None, **overrides):
        fields = {"name": "Python", "category": Skill.Category.LANGUAGE}
        fields.update(overrides)
        return Skill.objects.create(profile=profile or self.profile, **fields)

    def make_education(self, profile=None, **overrides):
        fields = {"institution": "UoN", "qualification": "BSc", "field_of_study": "CS"}
        fields.update(overrides)
        return Education.objects.create(profile=profile or self.profile, **fields)

    def make_project(self, profile=None, **overrides):
        fields = {
            "name": "Kazi",
            "description": "d",
            "role": "r",
            "technologies": "Python",
        }
        fields.update(overrides)
        return Project.objects.create(profile=profile or self.profile, **fields)

    def other_profile(self):
        other = User.objects.create_user("bob", "bob@example.com", PASSWORD)
        return CareerProfile.objects.create(user=other, full_name="Bob")

    # --- access and adding ---

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_add_skill(self):
        response = self.client.post(self.url, self.valid_data(), follow=True)
        self.assertRedirects(response, self.url)
        self.assertContains(response, "Skill added.")
        skill = Skill.objects.get()
        self.assertEqual(skill.profile, self.profile)
        self.assertFalse(skill.is_confirmed)

    def test_required_fields(self):
        for field in ["name", "category"]:
            with self.subTest(field=field):
                response = self.client.post(self.url, self.valid_data(**{field: ""}))
                self.assertEqual(response.status_code, 200)
                self.assertFormError(response.context["form"], field, "This field is required.")
        self.assertEqual(Skill.objects.count(), 0)

    def test_name_is_trimmed(self):
        self.client.post(self.url, self.valid_data(name="  Python  "))
        self.assertEqual(Skill.objects.get().name, "Python")

    # --- duplicates ---

    def test_duplicate_name_rejected_ignoring_case(self):
        self.make_skill(name="Python")
        response = self.client.post(self.url, self.valid_data(name="python"))
        self.assertFormError(
            response.context["form"], "name", "You already have a skill with this name."
        )
        self.assertEqual(Skill.objects.count(), 1)

    def test_same_name_allowed_for_another_user(self):
        self.make_skill(profile=self.other_profile(), name="Python")
        self.client.post(self.url, self.valid_data(name="Python"))
        self.assertEqual(Skill.objects.filter(profile=self.profile).count(), 1)

    def test_edit_to_another_existing_name_rejected(self):
        self.make_skill(name="Python")
        skill = self.make_skill(name="Django", category=Skill.Category.FRAMEWORK)
        response = self.client.post(
            reverse("skill_edit", args=[skill.pk]),
            self.valid_data(name="PYTHON", category=Skill.Category.FRAMEWORK),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.context["form"].errors)
        skill.refresh_from_db()
        self.assertEqual(skill.name, "Django")

    def test_edit_keeping_own_name_is_not_a_duplicate(self):
        skill = self.make_skill(name="Python")
        response = self.client.post(
            reverse("skill_edit", args=[skill.pk]), self.valid_data(notes="Used daily")
        )
        self.assertRedirects(response, self.url)
        skill.refresh_from_db()
        self.assertEqual(skill.notes, "Used daily")

    # --- supporting evidence ---

    def test_add_with_supporting_entries(self):
        edu = self.make_education()
        proj = self.make_project()
        self.client.post(
            self.url,
            self.valid_data(supporting_education=[edu.pk], supporting_projects=[proj.pk]),
        )
        skill = Skill.objects.get()
        self.assertEqual(list(skill.supporting_education.all()), [edu])
        self.assertEqual(list(skill.supporting_projects.all()), [proj])

    def test_cannot_link_another_users_entry(self):
        other_edu = self.make_education(profile=self.other_profile())
        response = self.client.post(
            self.url, self.valid_data(supporting_education=[other_edu.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("supporting_education", response.context["form"].errors)
        self.assertEqual(Skill.objects.count(), 0)

    def test_claimed_without_links(self):
        self.assertFalse(self.make_skill().is_supported)

    def test_unconfirmed_link_does_not_support(self):
        skill = self.make_skill()
        skill.supporting_projects.add(self.make_project(is_confirmed=False))
        self.assertFalse(skill.is_supported)

    def test_confirmed_link_supports(self):
        skill = self.make_skill()
        skill.supporting_projects.add(self.make_project(is_confirmed=True))
        self.assertTrue(skill.is_supported)

    def test_list_shows_claimed_and_supported(self):
        self.make_skill(name="Claimed one", category=Skill.Category.TOOL)
        supported = self.make_skill(name="Supported one")
        supported.supporting_projects.add(self.make_project(is_confirmed=True))
        response = self.client.get(self.url)
        self.assertContains(response, "Claimed")
        self.assertContains(response, "Supported")

    # --- confirm, edit, remove ---

    def test_confirm_toggle(self):
        skill = self.make_skill()
        url = reverse("skill_confirm", args=[skill.pk])
        response = self.client.post(url, follow=True)
        self.assertContains(response, "Skill confirmed.")
        skill.refresh_from_db()
        self.assertTrue(skill.is_confirmed)
        response = self.client.post(url, follow=True)
        self.assertContains(response, "Skill marked unconfirmed.")

    def test_confirm_requires_post(self):
        skill = self.make_skill()
        response = self.client.get(reverse("skill_confirm", args=[skill.pk]))
        self.assertEqual(response.status_code, 405)

    def test_edit_form_shows_saved_values(self):
        skill = self.make_skill(proficiency=Skill.Proficiency.ADVANCED)
        response = self.client.get(reverse("skill_edit", args=[skill.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].initial["proficiency"], "advanced")

    def test_unchanged_save_keeps_confirmation(self):
        skill = self.make_skill(is_confirmed=True)
        response = self.client.post(
            reverse("skill_edit", args=[skill.pk]), self.valid_data(), follow=True
        )
        self.assertContains(response, "Skill updated.")
        skill.refresh_from_db()
        self.assertTrue(skill.is_confirmed)

    def test_changed_save_resets_confirmation(self):
        skill = self.make_skill(is_confirmed=True)
        response = self.client.post(
            reverse("skill_edit", args=[skill.pk]),
            self.valid_data(proficiency=Skill.Proficiency.EXPERT),
            follow=True,
        )
        self.assertContains(response, "please confirm it again")
        skill.refresh_from_db()
        self.assertFalse(skill.is_confirmed)

    def test_changing_only_links_resets_confirmation(self):
        skill = self.make_skill(is_confirmed=True)
        proj = self.make_project()
        self.client.post(
            reverse("skill_edit", args=[skill.pk]),
            self.valid_data(supporting_projects=[proj.pk]),
        )
        skill.refresh_from_db()
        self.assertFalse(skill.is_confirmed)
        self.assertEqual(list(skill.supporting_projects.all()), [proj])

    def test_delete_skill(self):
        skill = self.make_skill()
        response = self.client.post(reverse("skill_delete", args=[skill.pk]), follow=True)
        self.assertContains(response, "Skill removed.")
        self.assertEqual(Skill.objects.count(), 0)

    def test_delete_requires_post(self):
        skill = self.make_skill()
        response = self.client.get(reverse("skill_delete", args=[skill.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Skill.objects.count(), 1)

    def test_deleting_linked_entry_keeps_skill(self):
        skill = self.make_skill()
        proj = self.make_project(is_confirmed=True)
        skill.supporting_projects.add(proj)
        proj.delete()
        skill.refresh_from_db()
        self.assertFalse(skill.is_supported)

    def test_other_users_skill_is_404(self):
        skill = self.make_skill(profile=self.other_profile(), name="Secret")
        for name, method in [
            ("skill_edit", self.client.get),
            ("skill_edit", self.client.post),
            ("skill_confirm", self.client.post),
            ("skill_delete", self.client.post),
        ]:
            with self.subTest(view=name, method=method.__name__):
                self.assertEqual(method(reverse(name, args=[skill.pk])).status_code, 404)
        self.assertEqual(Skill.objects.count(), 1)


class CertificationPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("amina", "amina@example.com", PASSWORD)
        self.client.force_login(self.user)
        self.profile = CareerProfile.objects.create(user=self.user, full_name="Amina Otieno")
        self.url = reverse("certification_list")

    def valid_data(self, **overrides):
        data = {
            "name": "Google Data Analytics",
            "provider": "Coursera",
            "issue_date": "2026-03-15",
            "expiry_date": "",
            "url": "https://coursera.org/verify/abc",
            "description": "SQL, R and Tableau.",
        }
        data.update(overrides)
        return data

    def make_entry(self, profile=None, **overrides):
        fields = {
            "name": "Google Data Analytics",
            "provider": "Coursera",
            "issue_date": date(2026, 3, 15),
        }
        fields.update(overrides)
        return Certification.objects.create(profile=profile or self.profile, **fields)

    def other_entry(self):
        other = User.objects.create_user("bob", "bob@example.com", PASSWORD)
        other_profile = CareerProfile.objects.create(user=other, full_name="Bob")
        return self.make_entry(profile=other_profile, name="Bob's cert")

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_add_entry(self):
        response = self.client.post(self.url, self.valid_data(), follow=True)
        self.assertRedirects(response, self.url)
        self.assertContains(response, "Certification added.")
        entry = Certification.objects.get()
        self.assertEqual(entry.profile, self.profile)
        self.assertEqual(entry.issue_date, date(2026, 3, 15))
        self.assertFalse(entry.is_confirmed)

    def test_required_fields(self):
        for field in ["name", "provider", "issue_date"]:
            with self.subTest(field=field):
                response = self.client.post(self.url, self.valid_data(**{field: ""}))
                self.assertEqual(response.status_code, 200)
                self.assertFormError(response.context["form"], field, "This field is required.")
        self.assertEqual(Certification.objects.count(), 0)

    def test_optional_fields_blank(self):
        self.client.post(self.url, self.valid_data(url="", description=""))
        entry = Certification.objects.get()
        self.assertIsNone(entry.expiry_date)
        self.assertEqual(entry.url, "")

    def test_invalid_url_rejected(self):
        response = self.client.post(self.url, self.valid_data(url="not a url"))
        self.assertIn("url", response.context["form"].errors)
        self.assertEqual(Certification.objects.count(), 0)

    def test_expiry_before_issue_rejected(self):
        response = self.client.post(
            self.url, self.valid_data(issue_date="2026-03-15", expiry_date="2026-01-01")
        )
        self.assertFormError(
            response.context["form"],
            "expiry_date",
            "Expiry date cannot be before the issue date.",
        )
        self.assertEqual(Certification.objects.count(), 0)

    def test_equal_issue_and_expiry_allowed(self):
        self.client.post(
            self.url, self.valid_data(issue_date="2026-03-15", expiry_date="2026-03-15")
        )
        self.assertEqual(Certification.objects.count(), 1)

    def test_newest_issue_date_first(self):
        self.make_entry(name="Old", issue_date=date(2024, 1, 1))
        self.make_entry(name="New", issue_date=date(2026, 1, 1))
        response = self.client.get(self.url)
        self.assertEqual([e.name for e in response.context["entries"]], ["New", "Old"])

    def test_list_shows_only_own_entries(self):
        self.make_entry(name="Mine")
        self.other_entry()
        response = self.client.get(self.url)
        self.assertContains(response, "Mine")
        self.assertNotContains(response, "Bob&#x27;s cert")

    def test_confirm_toggle(self):
        entry = self.make_entry()
        url = reverse("certification_confirm", args=[entry.pk])
        response = self.client.post(url, follow=True)
        self.assertContains(response, "Certification confirmed.")
        entry.refresh_from_db()
        self.assertTrue(entry.is_confirmed)
        response = self.client.post(url, follow=True)
        self.assertContains(response, "Certification marked unconfirmed.")

    def test_edit_form_shows_saved_dates(self):
        entry = self.make_entry(expiry_date=date(2029, 3, 15))
        response = self.client.get(reverse("certification_edit", args=[entry.pk]))
        self.assertContains(response, 'value="2026-03-15"')
        self.assertContains(response, 'value="2029-03-15"')

    def test_unchanged_save_keeps_confirmation(self):
        entry = self.make_entry(
            is_confirmed=True, url="https://coursera.org/verify/abc", description="SQL, R and Tableau."
        )
        self.client.post(reverse("certification_edit", args=[entry.pk]), self.valid_data())
        entry.refresh_from_db()
        self.assertTrue(entry.is_confirmed)

    def test_changed_save_resets_confirmation(self):
        entry = self.make_entry(is_confirmed=True)
        response = self.client.post(
            reverse("certification_edit", args=[entry.pk]),
            self.valid_data(provider="edX"),
            follow=True,
        )
        self.assertContains(response, "please confirm it again")
        entry.refresh_from_db()
        self.assertFalse(entry.is_confirmed)
        self.assertEqual(entry.provider, "edX")

    def test_delete_entry(self):
        entry = self.make_entry()
        response = self.client.post(reverse("certification_delete", args=[entry.pk]), follow=True)
        self.assertContains(response, "Certification removed.")
        self.assertEqual(Certification.objects.count(), 0)

    def test_delete_requires_post(self):
        entry = self.make_entry()
        response = self.client.get(reverse("certification_delete", args=[entry.pk]))
        self.assertEqual(response.status_code, 405)

    def test_other_users_entry_is_404(self):
        entry = self.other_entry()
        for name, method in [
            ("certification_edit", self.client.get),
            ("certification_edit", self.client.post),
            ("certification_confirm", self.client.post),
            ("certification_delete", self.client.post),
        ]:
            with self.subTest(view=name, method=method.__name__):
                self.assertEqual(method(reverse(name, args=[entry.pk])).status_code, 404)
        self.assertEqual(Certification.objects.count(), 1)

    def test_dashboard_links_to_page(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, self.url)


class AchievementPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("amina", "amina@example.com", PASSWORD)
        self.client.force_login(self.user)
        self.profile = CareerProfile.objects.create(user=self.user, full_name="Amina Otieno")
        self.url = reverse("achievement_list")

    def valid_data(self, **overrides):
        data = {
            "title": "Dean's List",
            "issuer": "University of Nairobi",
            "date": "2026-06-30",
            "description": "Top 5% of the class.",
            "url": "",
        }
        data.update(overrides)
        return data

    def make_entry(self, profile=None, **overrides):
        fields = {
            "title": "Dean's List",
            "issuer": "University of Nairobi",
            "date": date(2026, 6, 30),
        }
        fields.update(overrides)
        return Achievement.objects.create(profile=profile or self.profile, **fields)

    def other_entry(self):
        other = User.objects.create_user("bob", "bob@example.com", PASSWORD)
        other_profile = CareerProfile.objects.create(user=other, full_name="Bob")
        return self.make_entry(profile=other_profile, title="Bob's award")

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_add_entry(self):
        response = self.client.post(self.url, self.valid_data(), follow=True)
        self.assertRedirects(response, self.url)
        self.assertContains(response, "Achievement added.")
        entry = Achievement.objects.get()
        self.assertEqual(entry.profile, self.profile)
        self.assertEqual(entry.date, date(2026, 6, 30))
        self.assertFalse(entry.is_confirmed)

    def test_required_fields_including_date(self):
        for field in ["title", "issuer", "date"]:
            with self.subTest(field=field):
                response = self.client.post(self.url, self.valid_data(**{field: ""}))
                self.assertEqual(response.status_code, 200)
                self.assertFormError(response.context["form"], field, "This field is required.")
        self.assertEqual(Achievement.objects.count(), 0)

    def test_optional_fields_blank(self):
        self.client.post(self.url, self.valid_data(description="", url=""))
        entry = Achievement.objects.get()
        self.assertEqual(entry.description, "")
        self.assertEqual(entry.url, "")

    def test_invalid_url_rejected(self):
        response = self.client.post(self.url, self.valid_data(url="not a url"))
        self.assertIn("url", response.context["form"].errors)

    def test_newest_first_and_undated_last(self):
        self.make_entry(title="Old", date=date(2024, 1, 1))
        self.make_entry(title="Undated", date=None)
        self.make_entry(title="New", date=date(2026, 1, 1))
        response = self.client.get(self.url)
        self.assertEqual(
            [e.title for e in response.context["entries"]], ["New", "Old", "Undated"]
        )

    def test_confirm_toggle(self):
        entry = self.make_entry()
        url = reverse("achievement_confirm", args=[entry.pk])
        response = self.client.post(url, follow=True)
        self.assertContains(response, "Achievement confirmed.")
        entry.refresh_from_db()
        self.assertTrue(entry.is_confirmed)
        response = self.client.post(url, follow=True)
        self.assertContains(response, "Achievement marked unconfirmed.")

    def test_edit_form_shows_saved_date(self):
        entry = self.make_entry()
        response = self.client.get(reverse("achievement_edit", args=[entry.pk]))
        self.assertContains(response, 'value="2026-06-30"')

    def test_undated_entry_must_get_a_date_when_edited(self):
        entry = self.make_entry(date=None)
        response = self.client.post(
            reverse("achievement_edit", args=[entry.pk]), self.valid_data(date="")
        )
        self.assertFormError(response.context["form"], "date", "This field is required.")

    def test_unchanged_save_keeps_confirmation(self):
        entry = self.make_entry(is_confirmed=True, description="Top 5% of the class.")
        self.client.post(reverse("achievement_edit", args=[entry.pk]), self.valid_data())
        entry.refresh_from_db()
        self.assertTrue(entry.is_confirmed)

    def test_changed_save_resets_confirmation(self):
        entry = self.make_entry(is_confirmed=True)
        response = self.client.post(
            reverse("achievement_edit", args=[entry.pk]),
            self.valid_data(issuer="Strathmore"),
            follow=True,
        )
        self.assertContains(response, "please confirm it again")
        entry.refresh_from_db()
        self.assertFalse(entry.is_confirmed)

    def test_delete_entry(self):
        entry = self.make_entry()
        response = self.client.post(reverse("achievement_delete", args=[entry.pk]), follow=True)
        self.assertContains(response, "Achievement removed.")
        self.assertEqual(Achievement.objects.count(), 0)

    def test_delete_requires_post(self):
        entry = self.make_entry()
        response = self.client.get(reverse("achievement_delete", args=[entry.pk]))
        self.assertEqual(response.status_code, 405)

    def test_other_users_entry_is_404(self):
        entry = self.other_entry()
        for name, method in [
            ("achievement_edit", self.client.get),
            ("achievement_edit", self.client.post),
            ("achievement_confirm", self.client.post),
            ("achievement_delete", self.client.post),
        ]:
            with self.subTest(view=name, method=method.__name__):
                self.assertEqual(method(reverse(name, args=[entry.pk])).status_code, 404)
        self.assertEqual(Achievement.objects.count(), 1)

    def test_dashboard_links_to_page(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, self.url)