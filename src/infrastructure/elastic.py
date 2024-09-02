from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import Q

from config import settings

from .models import Industry, Project, Technology


@registry.register_document
class ProjectDocument(Document):
    industries = fields.ObjectField(
        properties={
            "title": fields.TextField(),
        }
    )
    technologies = fields.ObjectField(
        properties={
            "title": fields.TextField(),
        }
    )

    class Index:
        name = "projects"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Project
        fields = [
            "title",
            "description",
            "created_at",
            "updated_at",
        ]
        related_models = [Industry, Technology]

    def get_queryset(self):
        return (
            super(ProjectDocument, self)
            .get_queryset()
            .select_related("user")
            .prefetch_related("industries", "technologies")
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Industry):
            return related_instance.projects.all()
        elif isinstance(related_instance, Technology):
            return related_instance.projects.all()


def search_projects(
    user,
    search_string=None,
    technology_filters=None,
    industry_filters=None,
    page=settings.DEFAULT_SIZE_PAGE,
    size=settings.DEFAULT_FIRST_PAGE,
    sort_by=None,
):
    search = ProjectDocument.search()

    search = search.filter("term", user=user.id)

    if search_string:
        search = search.query(
            Q("multi_match", query=search_string, fields=["title", "description"])
        )

    if technology_filters:
        search = search.filter("terms", technology=technology_filters)
    if industry_filters:
        search = search.filter("terms", industry=industry_filters)

    search.aggs.bucket("technologies", "terms", field="technology")
    search.aggs.bucket("industries", "terms", field="industry")

    search = search[(page - 1) * size : page * size]

    if sort_by:
        search = search.sort({sort_by: {"order": "asc"}})

    search.aggs.bucket("technologies", "terms", field="technology")
    search.aggs.bucket("industries", "terms", field="industry")

    response = search.execute()

    facets = {
        "technologies": [
            (bucket.key, bucket.doc_count)
            for bucket in response.aggregations.technologies.buckets
        ],
        "industries": [
            (bucket.key, bucket.doc_count)
            for bucket in response.aggregations.industries.buckets
        ],
    }

    return response, facets
