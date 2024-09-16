import os

from django.urls import reverse
from elasticsearch.helpers import bulk
from rest_framework import status

from accounts.tests.test_views import BaseViewTests
from infrastructure.elastic import ProjectDocument
from infrastructure.models import Project


class IndexViewTests(BaseViewTests):
    def setUp(self):
        super(IndexViewTests, self).setUp()
        self.project = Project.objects.create(
            user_id=self.u1.id,
            title="Test Project",
            description="Test Description",
            url="http://example.com",
        )
        projects_to_index = Project.objects.all()
        actions = (
            ProjectDocument.get_indexing_action(project)
            for project in projects_to_index
        )
        bulk(self.es, actions)

        self.es.indices.refresh(index=self.index_name)

    def test_index_view(self):
        self.client.force_login(self.u1)
        response = self.client.get(reverse("index"), {"q": "test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, "index.html")
        self.assertIn("results", response.context)
        self.assertEqual(response.context["total_results"], 1)


class UploadCSVViewTests(BaseViewTests):
    def test_upload_csv_view_valid(self):
        self.client.force_login(self.u1)
        csv_content = """title;description;url;industries;technologies
        According early somebody interest size environment accept.;Leader describe door Mrs. Church throw step about responsibility system its relate. Interesting party happy onto under.;;Energy,Biotechnology,Logistics;Docker,Chef"""
        csv_path = "test.csv"
        with open(csv_path, "w") as f:
            f.write(csv_content)

        with open(csv_path, "rb") as f:
            response = self.client.post(reverse("upload_csv"), {"csv_file": f})

        os.remove(csv_path)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse("index"))
        self.es.indices.refresh(index=self.index_name)
        self.assertTrue(self.es.exists(index=self.index_name, id=1))
