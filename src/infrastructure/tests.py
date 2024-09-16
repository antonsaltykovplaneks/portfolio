import json
import uuid
from django.urls import reverse
from unittest import mock
from rest_framework import status

from accounts.tests.test_views import BaseViewTests
from .models import (
    Industry,
    ProjectSet,
    ProjectSetLink,
    ProjectSetLinkAccess,
    Project,
    Technology,
)


class ProjectSetDetailViewTests(BaseViewTests):
    def setUp(self):
        super(ProjectSetDetailViewTests, self).setUp()

        self.project_set = ProjectSet.objects.create(
            title="Test Project Set", user=self.u1
        )
        self.project_set_link = ProjectSetLink.objects.create(
            project_set=self.project_set, uuid=uuid.uuid4()
        )
        self.project = Project.objects.create(
            user_id=self.u1.id,
            title="Test Project",
            description="Test Description",
            url="http://example.com",
        )
        self.project_set.projects.add(self.project)
        self.project_set_access = ProjectSetLinkAccess.objects.create(
            project_set=self.project_set, ip_address_hash="test-hash"
        )

    @mock.patch("infrastructure.views.send_open_notification_email.delay")
    def test_get_project_set_detail(self, mock_send_task):
        mock_send_task.return_value = None

        self.client.force_login(self.u1)
        response = self.client.get(
            reverse(
                "project_set",
                kwargs={"project_set_id": self.project_set_link.uuid},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_task.assert_called_once_with(self.u1.email, self.project_set.title)
        self.assertTemplateUsed(response, "sets/set.html")
        self.assertEqual(response.context["project_set"], self.project_set)

    def test_delete_project_set(self):
        self.client.force_login(self.u1)
        response = self.client.delete(
            reverse("project_set", kwargs={"project_set_id": self.project_set.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "success"})
        with self.assertRaises(ProjectSet.DoesNotExist):
            ProjectSet.objects.get(id=self.project_set.id)

    def test_put_project_set(self):
        self.client.force_login(self.u1)
        new_title = "Updated Project Set"
        new_project = Project.objects.create(
            title="New Project",
            description="New Description",
            url="http://newexample.com",
            user_id=self.u1.id,
        )
        response = self.client.put(
            reverse("project_set", kwargs={"project_set_id": self.project_set.id}),
            data=json.dumps({"title": new_title, "projects": [new_project.id]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "success"})
        self.project_set.refresh_from_db()
        self.assertEqual(self.project_set.title, new_title)
        self.assertIn(new_project, self.project_set.projects.all())

        # negative test case
        response = self.client.put(
            reverse("project_set", kwargs={"project_set_id": self.project_set.id}),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProjectViewTests(BaseViewTests):
    def setUp(self):
        super(ProjectViewTests, self).setUp()
        self.technology = Technology.objects.all().first()
        self.industry = Industry.objects.all().first()
        self.project = Project.objects.create(
            user_id=self.u1.id,
            title="Test Project",
            description="Test Description",
            url="http://example.com",
        )

    def test_put_project(self):
        self.client.force_login(self.u1)
        new_title = "Updated Project"
        new_description = "Updated Description"
        new_url = "http://updatedexample.com"
        response = self.client.put(
            reverse("project", kwargs={"project_id": self.project.id}),
            data=json.dumps(
                {
                    "title": new_title,
                    "description": new_description,
                    "url": new_url,
                    "technologies": [self.technology.id],
                    "industries": [self.industry.id],
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "success"})
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, new_title)
        self.assertEqual(self.project.description, new_description)
        self.assertEqual(self.project.url, new_url)
        self.assertIn(self.technology, self.project.technologies.all())
        self.assertIn(self.industry, self.project.industries.all())

    def test_delete_project(self):
        self.client.force_login(self.u1)
        response = self.client.delete(
            reverse("project", kwargs={"project_id": self.project.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "success"})
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=self.project.id)


class ProjectSetViewTests(BaseViewTests):
    def setUp(self):
        super(ProjectSetViewTests, self).setUp()
        self.project = Project.objects.create(
            user_id=self.u1.id,
            title="Test Project",
            description="Test Description",
            url="http://example.com",
        )

    def test_post_project_set(self):
        self.client.force_login(self.u1)
        response = self.client.post(
            reverse("project_set_list"),
            data=json.dumps(
                {"title": "New Project Set", "projects": [self.project.id]}
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "success"})
        project_set = ProjectSet.objects.get(title="New Project Set")
        self.assertIn(self.project, project_set.projects.all())

    def test_get_project_set_list(self):
        self.client.force_login(self.u1)
        ProjectSet.objects.create(title="Test Project Set", user=self.u1)
        response = self.client.get(reverse("project_set_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, "sets/list_sets.html")
        self.assertIn("project_sets", response.context)
        self.assertEqual(len(response.context["project_sets"]), 1)
