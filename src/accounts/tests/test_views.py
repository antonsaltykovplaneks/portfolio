from unittest import mock
from unittest.mock import patch

from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from elasticsearch.helpers import bulk
from elasticsearch_dsl.connections import connections

from infrastructure.elastic import ProjectDocument
from infrastructure.mocking import IndustryFactory, TechnologyFactory

from ..models import User


class BaseViewTests(TestCase):
    def setUp(self):
        self.es = connections.get_connection()
        TechnologyFactory.import_json()
        IndustryFactory.import_json()
        self.u1 = User.objects.create_user("demo@mail.com", "John Doe", "demo")

        self.index_name = ProjectDocument.Index.name

        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)

        ProjectDocument.init()

    def index_projects(self, projects):
        actions = [
            {
                "_op_type": "index",
                "_index": self.index_name,
                "_id": project.id,
                "_source": {
                    "title": project.title,
                    "description": project.description,
                    "user_id": project.user_id,
                    "technologies": project.technologies,
                    "industries": project.industries,
                },
            }
            for project in projects
        ]
        bulk(self.es, actions)
        self.es.indices.refresh(index=self.index_name)

    def tearDown(self):
        connections.get_connection().indices.delete(index="*")


class PersonalInformationViewTests(BaseViewTests):
    def setUp(self):
        super(PersonalInformationViewTests, self).setUp()

    def test_personal_information_view(self):
        self.client.force_login(self.u1)
        response = self.client.get(reverse("personal_information"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/personal_information.html")
        self.assertEqual(response.context["user"], self.u1)

    @mock.patch("accounts.views.send_email_celery_task.delay")
    def test_personal_information_edit_view(self, mock_send_task):
        mock_send_task.return_value = None

        self.client.force_login(self.u1)
        response = self.client.post(
            reverse("edit_personal_information"),
            data={"email": "newemail@mail.com", "name": "John Doe"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/personal_information.html")
        mock_send_task.assert_called_once_with(self.u1.id)

        self.u1.refresh_from_db()
        self.assertEqual(self.u1.email, "newemail@mail.com")


class AuthViewsTests(BaseViewTests):
    def setUp(self):
        super(AuthViewsTests, self).setUp()

    def test_login_view(self):
        response = self.client.post(
            reverse("login"),
            data={"username": "demo@mail.com", "password": "demo"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.redirect_chain,
            [(reverse("index"), 302)],
        )

        self.assertTrue(response.context["user"].is_active)
        self.assertEqual(response.context["user"], self.u1)

    @mock.patch("accounts.views.send_email_celery_task.delay")
    def test_register_view(self, mock_send_task):
        mock_send_task.return_value = None

        response = self.client.post(
            reverse("register"),
            data={
                "email": "newuser@mail.com",
                "name": "New User",
                "password1": "newpassword",
                "password2": "newpassword",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        new_user = User.objects.get(email="newuser@mail.com")
        self.assertEqual(new_user.name, "New User")
        mock_send_task.assert_called_once_with(new_user.id)

    def test_logout_view(self):
        self.client.force_login(self.u1)
        response = self.client.get(reverse("logout"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)

    def test_verify_email(self):
        token = default_token_generator.make_token(self.u1)
        uid = urlsafe_base64_encode(force_bytes(self.u1.pk))
        response = self.client.get(
            reverse("verify_email", kwargs={"uidb64": uid, "token": token})
        )
        self.assertEqual(response.status_code, 200)
        self.u1.refresh_from_db()
        self.assertTrue(self.u1.is_verified)

    def test_linkedin_login(self):
        response = self.client.get(reverse("linkedin_login"))
        self.assertEqual(response.status_code, 302)
