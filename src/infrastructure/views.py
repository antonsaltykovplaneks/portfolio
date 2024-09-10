import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from rest_framework import generics

from infrastructure.models import Industry, Project, ProjectSet, Technology
from infrastructure.serializers import IndustrySerializer, TechnologySerializer


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


class ProjectView(View):
    def put(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        data = json.loads(request.body)

        title = data.get("title")
        description = data.get("description")
        technology_ids = data.get("technologies")
        industry_ids = data.get("industries")
        url = data.get("url")

        if title:
            project.title = title
        if description:
            project.description = description
        if technology_ids:
            project.technologies.clear()
            for tech_id in technology_ids:
                tech_obj = Technology.objects.filter(id=tech_id).first()
                project.technologies.add(tech_obj)
        if industry_ids:
            project.industries.clear()
            for industry_id in industry_ids:
                industry_obj = Industry.objects.filter(id=industry_id).first()
                project.industries.add(industry_obj)
        if url:
            project.url = url

        project.save()

        return JsonResponse({"status": "success"})


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


class IndustryListView(generics.ListAPIView):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer


class TechnologyListView(generics.ListAPIView):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
