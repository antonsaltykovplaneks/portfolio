from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import Q, analyzer

from config import settings

from .models import Industry, Project, Technology

html_strip = analyzer(
    "html_strip",
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"],
)


@registry.register_document
class ProjectDocument(Document):
    industries = fields.TextField(
        attr="industries_indexing",
        analyzer=html_strip,
        fields={
            "raw": fields.KeywordField(),
            "suggest": fields.CompletionField(),
        },
    )

    technologies = fields.TextField(
        attr="technologies_indexing",
        analyzer=html_strip,
        fields={
            "raw": fields.KeywordField(),
            "suggest": fields.CompletionField(),
        },
    )

    user = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
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
            "url",
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
    page=settings.DEFAULT_FIRST_PAGE,
    size=settings.DEFAULT_SIZE_PAGE,
    sort_by=None,
):
    search = ProjectDocument.search()

    search = search.filter("term", user__id=user.id)

    if search_string:
        search = search.query(
            Q("multi_match", query=search_string, fields=["title", "description"])
        )

    if technology_filters:
        search = search.filter("terms", technology=technology_filters)
    if industry_filters:
        search = search.filter("terms", industry=industry_filters)

    search = search[(page - 1) * size : page * size]

    if sort_by:
        search = search.sort({sort_by: {"order": "asc"}})

    search.aggs.bucket("technologies", "terms", field="technologies.raw")
    search.aggs.bucket("industries", "terms", field="industries.raw")

    response = search.execute()

    technology_counts = {
        bucket.key: bucket.doc_count
        for bucket in response.aggregations.technologies.buckets
    }
    industry_counts = {
        bucket.key: bucket.doc_count
        for bucket in response.aggregations.industries.buckets
    }

    if technology_filters:
        technology_counts = {
            tech: count
            for tech, count in technology_counts.items()
            if count > 0 or tech in technology_filters
        }
    if industry_filters:
        industry_counts = {
            ind: count
            for ind, count in industry_counts.items()
            if count > 0 or ind in industry_filters
        }

    return {
        "data": response,
        "facets": {
            "technologies": technology_counts,
            "industries": industry_counts,
        },
    }
