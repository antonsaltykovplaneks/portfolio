from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import Q, analyzer
from typing import List

from config import settings

from .models import Industry, Project, Technology

# Define an analyzer to strip HTML tags and apply standard tokenization and filtering
html_strip = analyzer(
    "html_strip",
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"],
)


@registry.register_document
class ProjectDocument(Document):
    """
    Elasticsearch document for the Project model.
    """

    # Define fields for industries with custom analyzers and sub-fields
    industries = fields.TextField(
        attr="industries_indexing",
        analyzer=html_strip,
        fields={
            "raw": fields.KeywordField(),
            "suggest": fields.CompletionField(),
        },
    )

    # Define fields for technologies with custom analyzers and sub-fields
    technologies = fields.TextField(
        attr="technologies_indexing",
        analyzer=html_strip,
        fields={
            "raw": fields.KeywordField(),
            "suggest": fields.CompletionField(),
        },
    )

    # Define a nested field for user with specific properties
    user = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
        }
    )

    class Index:
        """
        Elasticsearch index settings.
        """

        name = "projects"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        """
        Django model settings for the Elasticsearch document.
        """

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
        """
        Override the default queryset to include related fields.
        """
        return (
            super(ProjectDocument, self)
            .get_queryset()
            .select_related("user")
            .prefetch_related("industries", "technologies")
        )

    def get_instances_from_related(self, related_instance):
        """
        Get instances of Project from related Industry or Technology instances.

        Args:
            related_instance: An instance of Industry or Technology.

        Returns:
            QuerySet of Project instances.
        """
        if isinstance(related_instance, Industry):
            return related_instance.projects.all()
        elif isinstance(related_instance, Technology):
            return related_instance.projects.all()


def search_projects(
    user,
    search_string: str = None,
    technology_filters: List[str] = None,
    industry_filters: List[str] = None,
    page: int = settings.DEFAULT_FIRST_PAGE,
    size: int = settings.DEFAULT_SIZE_PAGE,
    sort_by: str = None,
):
    """
    Search for projects in Elasticsearch.

    Args:
        user (_type_):The user performing the search.
        search_string (str, optional): The search query string. Defaults to None.
        technology_filters (List[str], optional): List of technology filters. Defaults to None.
        industry_filters (List[str], optional): List of industry filters. Defaults to None.
        page (int, optional):  The page number for pagination.. Defaults to settings.DEFAULT_FIRST_PAGE.
        size (int, optional): The number of results per page.. Defaults to settings.DEFAULT_SIZE_PAGE.
        sort_by (str, optional): The field to sort by.. Defaults to None.

    Returns:
        dict: A dictionary containing search results and facet counts.
    """
    search = ProjectDocument.search()

    search = search.filter("term", user__id=user.id)

    if search_string:
        search = search.query(
            Q("multi_match", query=search_string, fields=["title", "description"])
        )

    if technology_filters:
        # Apply "AND" logic by requiring all selected technologies to be present in each project
        for tech in technology_filters:
            search = search.filter("term", technologies__raw=tech)

    if industry_filters:
        # Apply "AND" logic by requiring all selected industries to be present in each project
        for ind in industry_filters:
            search = search.filter("term", industries__raw=ind)

    # Apply pagination
    search = search[(page - 1) * size : page * size]

    if sort_by:
        search = search.sort({sort_by: {"order": "asc"}})

    # Aggregate technology and industry counts
    search.aggs.bucket("technologies", "terms", field="technologies.raw")
    search.aggs.bucket("industries", "terms", field="industries.raw")

    response = search.execute()

    # Extract technology and industry counts from the response
    technology_counts = {
        bucket.key: bucket.doc_count
        for bucket in response.aggregations.technologies.buckets
    }
    industry_counts = {
        bucket.key: bucket.doc_count
        for bucket in response.aggregations.industries.buckets
    }

    # Filter out zero-count industries and technologies unless they were in the filters
    if industry_filters or technology_filters:
        industry_counts = {
            ind: count
            for ind, count in industry_counts.items()
            if count > 0 or ind in industry_filters
        }
        technology_counts = {
            tech: count
            for tech, count in technology_counts.items()
            if count > 0 or tech in technology_filters
        }

    return {
        "data": response,
        "facets": {
            "technologies": technology_counts,
            "industries": industry_counts,
        },
    }
