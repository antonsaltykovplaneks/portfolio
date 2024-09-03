from django.shortcuts import render

from infrastructure.elastic import search_projects
from config import settings


def project_search_view(request):
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

    return render(request, "index.html", {"results": results})
