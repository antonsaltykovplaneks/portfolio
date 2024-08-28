from unittest.mock import patch
from django.urls import reverse
from django.test import TestCase
from ..models import User


class BaseViewTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user("demo@mail.com", "John Doe", "demo")


class ProfileViewTests(BaseViewTests):
    def setUp(self):
        super(ProfileViewTests, self).setUp()

    def test_unauthorized_access(self):
        """Go to login page if unuauthorized user tries to open profile."""
        response = self.client.get(reverse("personal_information"), follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            [(a.replace("%2F", "/"), b) for a, b in response.redirect_chain],
            [(reverse("login"), 302)],
        )

    def test_authorized_access(self):
        """Check profile page for authorized user."""
        self.client.force_login(self.u1)
        response = self.client.get(reverse("personal_information"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["user"], self.u1)


class LoginViewTest(BaseViewTests):
    def setUp(self):
        super(LoginViewTest, self).setUp()

    def test_login_page_authorized(self):
        """Redirect to profile if user is already logged in."""
        self.client.force_login(self.u1)
        response = self.client.get(reverse("login"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain,
            [(reverse("index"), 302)],
        )

    def test_login_page_redirection_loop(self):
        """Raise exception if user tries to go to the /login/?next=/login/ page."""
        self.client.force_login(self.u1)
        with self.assertRaises(ValueError):
            self.client.get(reverse("login") + "?next=/login/", follow=True)

    def test_form_validation(self):
        response = self.client.post(
            reverse("login"),
            data={
                "username": "demo@mail.com",
                "password": "demo",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.redirect_chain,
            [(reverse("index"), 302)],
        )

        self.assertTrue(response.context["user"].is_active)
        self.assertEqual(response.context["user"], self.u1)


class RegisterViewTests(BaseViewTests):
    def setUp(self):
        super(RegisterViewTests, self).setUp()

    def test_as_authorized(self):
        self.client.force_login(self.u1)
        response = self.client.get(reverse("register"), follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.redirect_chain,
            [(reverse("index"), 302)],
        )

    def test_form_render(self):

        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 302)

    @patch('accounts.views.send_email_celery_task.delay')
    def test_form_validation(self, mock_send_email_task):
        response = self.client.post(
            reverse("register"),
            data={
                "email": "blah@mail.com",
                "name": "Emilia Clarke",
                "password1": "123456",
                "password2": "123456",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        mock_send_email_task.assert_called_once_with(User.objects.first().id)

        u = User.objects.get(email="blah@mail.com")
        self.assertEqual(u.name, "Emilia Clarke")
