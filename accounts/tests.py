from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

PASSWORD = "Kazi-Salama-2026!"


class RegisterTests(TestCase):
    def valid_data(self, **overrides):
        data = {
            "username": "amina",
            "email": "Amina@Example.com",
            "password1": PASSWORD,
            "password2": PASSWORD,
        }
        data.update(overrides)
        return data

    def test_register_page_loads(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create account")

    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(reverse("register"), self.valid_data())
        self.assertRedirects(response, reverse("profile_edit"))

        user = User.objects.get(username="amina")
        self.assertEqual(user.email, "amina@example.com")
        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_email_is_required(self):
        response = self.client.post(reverse("register"), self.valid_data(email=""))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())

    def test_duplicate_email_rejected_ignoring_case(self):
        User.objects.create_user("existing", "amina@example.com", PASSWORD)
        response = self.client.post(
            reverse("register"), self.valid_data(email="AMINA@example.com")
        )
        self.assertContains(response, "An account with this email already exists.")
        self.assertFalse(User.objects.filter(username="amina").exists())

    def test_signed_in_user_is_sent_to_dashboard(self):
        user = User.objects.create_user("amina", "amina@example.com", PASSWORD)
        self.client.force_login(user)
        response = self.client.get(reverse("register"))
        self.assertRedirects(response, reverse("dashboard"))


class AuthFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("amina", "amina@example.com", PASSWORD)

    def test_signed_out_visitor_is_sent_to_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_login_goes_to_profile(self):
        response = self.client.post(
            reverse("login"), {"username": "amina", "password": PASSWORD}
        )
        self.assertRedirects(response, reverse("profile_edit"))

    def test_wrong_password_shows_error(self):
        response = self.client.post(
            reverse("login"), {"username": "amina", "password": "wrong"}
        )
        self.assertContains(response, "Invalid username or password.")

    def test_logout_signs_out(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_page_links_to_register(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, reverse("register"))
