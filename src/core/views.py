from django.shortcuts import render

from infrastructure.elastic import search_projects
from config import settings


from urllib.parse import urlencode


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
