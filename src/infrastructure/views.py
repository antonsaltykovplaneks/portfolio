import json

from django.contrib import messages
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

    def delete(self, request, project_set_id):
        project_set = get_object_or_404(ProjectSet, pk=project_set_id)
        if project_set.user != request.user:
            messages.error(request, "Forbidden")
            return JsonResponse({"status": "error", "message": "Forbidden"}, status=403)
        project_set.delete()
        return JsonResponse({"status": "success"})

    def put(self, request, project_set_id):
        project_set = get_object_or_404(ProjectSet, pk=project_set_id)
        data = json.loads(request.body)
        title = data.get("title")
        project_ids = data.get("projects")

        if title and project_ids:
            project_set.title = title
            project_set.projects.clear()
            projects = Project.objects.filter(id__in=project_ids)
            for project in projects:
                project_set.add_project(project)
            project_set.save()

            return JsonResponse({"status": "success"})
        messages.error(request, "Invalid data")
        return JsonResponse({"status": "error", "message": "Invalid data"})


class ProjectSetView(View):
    def post(self, request):
        data = json.loads(request.body)
        title = data.get("title")
        project_ids = data.get("projects")

        if title and project_ids:
            project_set = ProjectSet.objects.create(title=title, user=request.user)
            projects = Project.objects.filter(id__in=project_ids)
            for project in projects:
                project_set.add_project(project)
            project_set.save()

            return JsonResponse({"status": "success"})

        messages.error(request, "Invalid data")
        return JsonResponse({"status": "error", "message": "Invalid data"})

    def get(self, request):
        project_sets = ProjectSet.objects.filter(user__id=request.user.id).all()
        return render(
            request,
            "sets/list_sets.html",
            {"project_sets": project_sets},
        )
