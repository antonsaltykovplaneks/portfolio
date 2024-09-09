from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import Q, analyzer
from typing import List

from config import settings
from collections import OrderedDict

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

        ignore_signals = True
        model = Project
        fields = [
            "id",
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

    @staticmethod
    def get_indexing_action(project):
        """
        Return the data necessary for bulk indexing of the given project.
        """
        return {
            "_op_type": "index",
            "_index": ProjectDocument.Index.name,
            "_id": project.id,
            "_source": {
                "title": project.title,
                "description": project.description,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
                "url": project.url,
                "industries": list(project.industries.values_list("title", flat=True)),
                "technologies": list(
                    project.technologies.values_list("title", flat=True)
                ),
                "user": {"id": project.user.id},
            },
        }


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
        user (_type_): The user performing the search.
        search_string (str, optional): The search query string. Defaults to None.
        technology_filters (List[str], optional): List of technology filters. Defaults to None.
        industry_filters (List[str], optional): List of industry filters. Defaults to None.
        page (int, optional): The page number for pagination. Defaults to settings.DEFAULT_FIRST_PAGE.
        size (int, optional): The number of results per page. Defaults to settings.DEFAULT_SIZE_PAGE.
        sort_by (str, optional): The field to sort by. Defaults to None.

    Returns:
        dict: A dictionary containing search results and facet counts.
    """
    search = ProjectDocument.search()

    search = search.filter("term", user__id=user.id)
    search.aggs.bucket("technologies", "terms", field="technologies.raw", size=10000)
    industries_agg = search.aggs.bucket("industries", "terms", field="industries.raw", size=10000)
    # Add a sub-aggregation to calculate potential projects if each industry filter is applied
    industries_agg.bucket(
        "potential_projects",
        "filter",
        filter=(
            ~Q("terms", industries__raw=industry_filters) if industry_filters else Q()
        ),
    )

    if search_string:
        search = search.query(
            Q(
                "multi_match",
                query=search_string,
                fields=["title", "description"],
                fuzziness="AUTO",  # Fuzziness for typo correction
            )
        )

    if technology_filters:
        # Apply "AND" logic by requiring all selected technologies to be present in each project
        for tech in technology_filters:
            search = search.filter("term", technologies__raw=tech)

    if industry_filters:
        search = search.filter("terms", industries__raw=industry_filters)
        industries_agg.bucket(
            "potential_projects",
            "filter",
            filter=~Q("terms", industries__raw=industry_filters),
        )
    # Apply pagination
    search = search[(page - 1) * size : page * size]

    if sort_by:
        search = search.sort({sort_by: {"order": "asc"}})

    # Aggregate technology and industry counts
    response = search.execute()

    technology_counts = OrderedDict(
        (bucket.key, bucket.doc_count)
        for bucket in response.aggregations.technologies.buckets
    )
    # Create industry counts with additional info on potential projects if filter is applied
    industry_counts = OrderedDict()
    for bucket in response.aggregations.industries.buckets:
        potential_count = bucket.potential_projects.doc_count + bucket.doc_count
        industry_counts[bucket.key] = {
            "count": bucket.doc_count,
            "potential_count": potential_count,
            "new_projects": potential_count - bucket.doc_count,
        }

    # Fetch all unique industries for the user to ensure they are always shown
    all_industries_search = ProjectDocument.search()
    all_industries_search = all_industries_search.filter("term", user__id=user.id)
    all_industries_search.aggs.bucket(
        "all_industries", "terms", field="industries.raw", size=10000
    )
    all_industries_response = all_industries_search.execute()

    all_industries = {
        bucket.key: bucket.doc_count
        for bucket in all_industries_response.aggregations.all_industries.buckets
    }

    # Ensure all industries are included in the final result
    for industry in all_industries.keys():
        if industry not in industry_counts:
            industry_counts[industry] = {
                "count": all_industries[industry],
                "potential_count": all_industries[industry],
                "new_projects": all_industries[industry],
            }

    # Filter out zero-count technologies unless they were in the filters
    if technology_filters:
        technology_counts = OrderedDict(
            (tech, count)
            for tech, count in technology_counts.items()
            if count > 0 or tech in technology_filters
        )

    # Sort the dictionaries by keys (alphabetical order)
    technology_counts = OrderedDict(sorted(technology_counts.items()))
    industry_counts = OrderedDict(sorted(industry_counts.items()))

    return {
        "data": response,
        "facets": {
            "technologies": technology_counts,
            "industries": industry_counts,
        },
    }
