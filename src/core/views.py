from urllib.parse import urlencode

import tablib
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from elasticsearch.helpers import bulk

from config import settings
from core.forms import CSVUploadForm
from infrastructure.admin import ProjectResource
from infrastructure.elastic import ProjectDocument, search_projects
from infrastructure.models import Project


def index(request):
    user = request.user
    search_string = request.GET.get("q")
    technologies = request.GET.getlist("technology")
    industries = request.GET.getlist("industry")
    page = int(request.GET.get("page", settings.DEFAULT_FIRST_PAGE))
    size = int(request.GET.get("size", settings.DEFAULT_SIZE_PAGE))
    sort_by = request.GET.get("sort_by")

    results = search_projects(
        user=user,
        search_string=search_string,
        technology_filters=technologies,
        industry_filters=industries,
        page=page,
        size=size,
        sort_by=sort_by,
    )

    total_results = results["data"].hits.total.value
    total_pages = (total_results + size - 1) // size  # Calculate total number of pages
    has_next_page = page < total_pages  # Determine if there is a next page

    # Manually build the query string, including all filter parameters
    query_params = {
        "q": search_string,
        "technology": technologies,
        "industry": industries,
        "size": size,
        "sort_by": sort_by,
    }
    query_string = urlencode(
        [
            (k, v)
            for k, vs in query_params.items()
            for v in (vs if isinstance(vs, list) else [vs])
            if v
        ]
    )

    context = {
        "results": results,
        "selected_industries": industries,
        "selected_technologies": technologies,
        "page": page,
        "size": size,
        "total_results": total_results,
        "page_range": (range(1, total_pages + 1) if total_pages > 1 else []),
        "has_next_page": has_next_page,
        "query_params": query_string,
    }

    return render(request, "index.html", context)


def upload_csv(request):
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["csv_file"]
            data = csv_file.read().decode("utf-8")
            dataset = tablib.Dataset().load(data, format="csv", delimiter=";")

            project_resource = ProjectResource()
            result = project_resource.import_data(
                dataset, dry_run=True, user_id=request.user.id
            )
            print(f"Dry run result: {result.totals}")

            if not result.has_errors():
                result = project_resource.import_data(
                    dataset, dry_run=False, user_id=request.user.id
                )
                print(f"Result: {result.totals}")
                created_or_updated_ids = set()
                for row_result in result.rows:
                    if row_result.import_type in ("new", "update"):
                        created_or_updated_ids.add(row_result.object_id)

                # Bulk indexing of only newly created or updated projects
                projects_to_index = Project.objects.filter(
                    id__in=created_or_updated_ids
                )
                actions = (
                    ProjectDocument.get_indexing_action(project)
                    for project in projects_to_index
                )
                index_result = bulk(ProjectDocument._get_connection(), actions)
                print(f"Indexing Result: {index_result}")
                messages.success(request, "CSV file imported and indexed successfully!")
                return redirect(reverse("index"))
            else:
                messages.error(request, "CSV file import failed due to errors.")
    else:
        form = CSVUploadForm()

    return render(request, "upload_csv.html", {"form": form})
