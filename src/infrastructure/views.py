import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from infrastructure.models import Project, ProjectSet


class ProjectSetDetailView(View):
    def get(self, request, project_set_id):
        project_set = get_object_or_404(ProjectSet, pk=project_set_id)
        return render(
            request,
            "sets/set.html",
            {"project_set": project_set},
        )


class ProjectSetView(View):
    def post(self, request):
        data = json.loads(request.body)
        title = data.get("title")
        project_ids = data.get("projects")

        if title and project_ids:
            project_set = ProjectSet.objects.create(title=title, user=request.user)
            projects = Project.objects.filter(id__in=project_ids)
            project_set.projects.add(*projects)
            project_set.save()

            return JsonResponse({"status": "success"})
        return JsonResponse({"status": "error", "message": "Invalid data"})

    def get(self, request):
        project_sets = ProjectSet.objects.filter(user__id=request.user.id).all()
        return render(
            request,
            "sets/list_sets.html",
            {"project_sets": project_sets},
        )
