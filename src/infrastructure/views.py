import hashlib
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from elasticsearch.helpers import bulk
from rest_framework import generics
from weasyprint import HTML

from infrastructure.elastic import ProjectDocument
from infrastructure.models import (
    EmailStatus,
    Industry,
    Project,
    ProjectSet,
    ProjectSetLink,
    ProjectSetLinkAccess,
    Technology,
)
from infrastructure.serializers import IndustrySerializer, TechnologySerializer
from infrastructure.tasks import send_open_notification_email, send_shared_set_email


@login_required
def download_pdf(request, project_set_id):
    project_set = ProjectSet.objects.get(id=project_set_id)
    project_set.increment_download_count()
    html_string = render_to_string(
        "sets/  pdf_template.html", {"project_set": project_set}
    )
    html = HTML(string=html_string)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{project_set.title}.pdf"'
    html.write_pdf(response)
    return response


@login_required
@require_http_methods(["GET"])
def get_project_sets_links(request):
    project_sets = ProjectSet.objects.filter(user=request.user).prefetch_related("link")

    project_sets_data = []

    for project_set in project_sets:
        links = (
            project_set.link.get_absolute_url() if hasattr(project_set, "link") else []
        )
        email_statuses = EmailStatus.objects.filter(project_set=project_set).values(
            "recipient_email", "status"
        )
        project_sets_data.append(
            {
                "id": project_set.id,
                "title": project_set.title,
                "download_count": project_set.download_count,
                "shared_link_count": project_set.shared_link_count,
                "links": [links],
                "email_statuses": list(email_statuses),
            }
        )

    return JsonResponse({"status": "success", "project_sets": project_sets_data})


@login_required
@require_http_methods(["DELETE"])
def delete_project_set_link(request):
    data = json.loads(request.body)
    project_set_link = data.get("link")
    # Extract the uuid from the link
    uuid = project_set_link.split("/")[-2]

    project_set_link = get_object_or_404(ProjectSetLink, uuid=uuid)
    project_set_link.delete()
    return JsonResponse({"status": "success"})


@login_required
@require_http_methods(["POST"])
def generate_project_set_link(request, project_set_id):
    project_set = get_object_or_404(ProjectSet, pk=project_set_id)
    link = project_set.get_or_create_link()
    return JsonResponse({"status": "success", "link": link})


@login_required
@require_http_methods(["POST"])
def share_to_email(request, project_set_id):
    data = json.loads(request.body)
    recipient_email = data.get("email")

    project_set = get_object_or_404(ProjectSet, pk=project_set_id)
    link = project_set.get_or_create_link()

    subject = f"Shared Project Set: {project_set.title}"
    body = f"You can access the project set using the following link: {link}"

    send_shared_set_email.delay(recipient_email, subject, body, project_set_id)

    return JsonResponse({"status": "success"})


class ProjectSetDetailView(View):
    def get(self, request, project_set_id):
        link = get_object_or_404(ProjectSetLink, uuid=project_set_id)
        project_set = link.project_set

        ip_address = request.META.get("REMOTE_ADDR")
        ip_address_hash = hashlib.sha256(ip_address.encode()).hexdigest()

        access_record, created = ProjectSetLinkAccess.objects.get_or_create(
            project_set=project_set,
            ip_address_hash=ip_address_hash,
        )

        access_record.view_count += 1
        access_record.save()

        if created:
            project_set.increment_shared_link_count()
            send_open_notification_email.delay(
                project_set.user.email, project_set.title
            )

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


@login_required
@require_http_methods(["POST"])
def add_project(request):
    data = json.loads(request.body)
    title = data.get("title")
    industries = data.get("industries", [])
    description = data.get("description")
    technologies = data.get("technologies", [])
    url = data.get("url", "")
    if Project.objects.filter(title=title, user=request.user).exists():
        return JsonResponse(
            {
                "status": "error",
                "message": "Project with the same title already exists",
            },
            status=400,
        )

    project = Project.objects.create(
        title=title, description=description, url=url, user=request.user
    )

    for technology_title in technologies:
        technology = Technology.objects.filter(title__iexact=technology_title).first()
        if not technology:
            technology = Technology.objects.create(title=technology_title)
        project.technologies.add(technology)

    for industry_title in industries:
        industry = Industry.objects.filter(title__iexact=industry_title).first()
        if not industry:
            industry = Industry.objects.create(title=industry_title)
        project.industries.add(industry)

    project.save()
    bulk(
        ProjectDocument._get_connection(),
        [ProjectDocument.get_indexing_action(project)],
    )
    return JsonResponse(
        {
            "status": "success",
            "project": {
                "id": project.id,
                "title": project.title,
                "industries": industries,
                "description": project.description,
                "technologies": technologies,
                "url": project.url,
            },
        }
    )


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
