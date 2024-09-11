import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from rest_framework import generics

from infrastructure.models import (
    Industry,
    Project,
    ProjectSet,
    ProjectSetLink,
    Technology,
)
from infrastructure.serializers import IndustrySerializer, TechnologySerializer


@login_required
@require_http_methods(["GET"])
def get_project_sets_links(request):
    project_sets = ProjectSet.objects.filter(user=request.user).prefetch_related(
        "links"
    )
    return JsonResponse(
        {
            "status": "success",
            "project_sets": [
                {
                    "id": project_set.id,
                    "title": project_set.title,
                    "links": [
                        link.get_absolute_url() for link in project_set.links.all()
                    ],
                }
                for project_set in project_sets
            ],
        }
    )


@login_required
@require_http_methods(["DELETE"])
def delete_project_set_link(request, project_set_link):
    project_set_link = get_object_or_404(ProjectSetLink, absolute_url=project_set_link)
    project_set_link.delete()
    return JsonResponse({"status": "success"})


@login_required
@require_http_methods(["POST"])
def generate_project_set_link(request, project_set_id):
    project_set = get_object_or_404(ProjectSet, pk=project_set_id)
    link = project_set.create_link()
    return JsonResponse({"status": "success", "link": link})


class ProjectSetDetailView(View):
    def get(self, request, project_set_id):
        link = get_object_or_404(ProjectSetLink, uuid=project_set_id)
        project_set = link.project_set
        return render(request, "sets/set.html", {"project_set": project_set})

    @method_decorator(login_required)
    def delete(self, request, project_set_id):
        project_set = get_object_or_404(
            ProjectSet, pk=project_set_id, user=request.user
        )
        project_set.delete()
        return JsonResponse({"status": "success"})

    @method_decorator(login_required)
    def put(self, request, project_set_id):
        project_set = get_object_or_404(
            ProjectSet, pk=project_set_id, user=request.user
        )
        data = json.loads(request.body)

        title = data.get("title")
        project_ids = data.get("projects")

        if not title or not project_ids:
            return JsonResponse(
                {"status": "error", "message": "Invalid data"}, status=400
            )

        project_set.title = title
        projects = Project.objects.filter(id__in=project_ids)
        project_set.projects.set(projects)
        project_set.save()

        return JsonResponse({"status": "success"})


@method_decorator(login_required, name="dispatch")
class ProjectView(View):
    def put(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        data = json.loads(request.body)

        project.title = data.get("title", project.title)
        project.description = data.get("description", project.description)
        project.url = data.get("url", project.url)

        technology_ids = data.get("technologies", [])
        industry_ids = data.get("industries", [])

        project.technologies.set(Technology.objects.filter(id__in=technology_ids))
        project.industries.set(Industry.objects.filter(id__in=industry_ids))
        project.save()

        return JsonResponse({"status": "success"})

    def delete(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        ProjectSet.objects.filter(projects__id=project_id).delete()
        project.delete()
        return JsonResponse({"status": "success"})


@method_decorator(login_required, name="dispatch")
class ProjectSetView(View):
    def post(self, request):
        data = json.loads(request.body)
        title = data.get("title")
        project_ids = data.get("projects")

        if not title or not project_ids:
            return JsonResponse(
                {"status": "error", "message": "Invalid data"}, status=400
            )

        project_set = ProjectSet.objects.create(title=title, user=request.user)
        projects = Project.objects.filter(id__in=project_ids)
        project_set.projects.set(projects)
        project_set.save()

        return JsonResponse({"status": "success"})

    def get(self, request):
        project_sets = ProjectSet.objects.filter(user=request.user)
        return render(request, "sets/list_sets.html", {"project_sets": project_sets})


class IndustryListView(generics.ListAPIView):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer


class TechnologyListView(generics.ListAPIView):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
