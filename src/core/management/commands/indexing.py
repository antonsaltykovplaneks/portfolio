from django.core.management.base import BaseCommand
from elasticsearch.helpers import bulk

from infrastructure.elastic import ProjectDocument
from infrastructure.models import Project


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Index all origin projects
        actions = (
            ProjectDocument.get_indexing_action(project)
            for project in Project.objects.filter(original_project__isnull=True).all()
        )
        index_result = bulk(ProjectDocument._get_connection(), actions)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully indexed {index_result[0]} documents")
        )
