from django.db import models
from django.urls import reverse
from uuid import uuid4

from config import settings


class Project(models.Model):
    class Meta:
        verbose_name_plural = "Projects"
        verbose_name = "Project"

    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="projects", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    url = models.URLField(null=True, blank=True)

    original_project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)

    industries = models.ManyToManyField("Industry", related_name="projects")
    technologies = models.ManyToManyField("Technology", related_name="projects")

    @property
    def is_diff_from_original(self):
        if not self.original_project:
            return False

        fields_to_compare = ["title", "description", "image", "url"]

        for field in fields_to_compare:
            if getattr(self, field) != getattr(self.original_project, field):
                return True

        if set(self.industries.all()) != set(self.original_project.industries.all()):
            return True

        if set(self.technologies.all()) != set(
            self.original_project.technologies.all()
        ):
            return True

        return False

    def create_copy(self, user):
        copy = Project.objects.create(
            title=self.title,
            description=self.description,
            image=self.image,
            url=self.url,
            original_project=self,
            user=user,
            updated_at=self.updated_at,
        )
        copy.industries.set(self.industries.all())
        copy.technologies.set(self.technologies.all())
        return copy

    def industries_indexing(self):
        return [industry.title for industry in self.industries.all()]

    def technologies_indexing(self):
        return [technology.title for technology in self.technologies.all()]

    def __str__(self):
        return self.title


class Industry(models.Model):
    class Meta:
        verbose_name_plural = "Industries"
        verbose_name = "Industry"

    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Technology(models.Model):
    class Meta:
        verbose_name_plural = "Technologies"
        verbose_name = "Technology"

    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Company(models.Model):
    class Meta:
        verbose_name_plural = "Companies"
        verbose_name = "Company"

    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class ProjectSet(models.Model):
    class Meta:
        verbose_name_plural = "Project sets"
        verbose_name = "Project set"

    title = models.CharField(max_length=255, help_text="Title of the project set")
    projects = models.ManyToManyField(
        "Project", related_name="project_sets", null=False
    )
    is_public = models.BooleanField(
        default=False, help_text="If the project set is public or not"
    )
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_link(self):
        if ProjectSetLink.objects.filter(project_set=self).exists():
            return ProjectSetLink.objects.get(project_set=self).absolute_url

    def get_or_create_link(self) -> str:
        if ProjectSetLink.objects.filter(project_set=self).exists():
            return ProjectSetLink.objects.get(project_set=self).absolute_url
        return ProjectSetLink.objects.create(project_set=self).absolute_url

    def add_project(self, project):
        project_copy = project.create_copy(self.user)
        self.projects.add(project_copy)

    def __str__(self):
        return self.title


class ProjectSetLink(models.Model):
    project_set = models.OneToOneField(
        "ProjectSet", on_delete=models.CASCADE, related_name="link"
    )
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)

    @property
    def absolute_url(self):
        return self.get_absolute_url()

    def get_absolute_url(self):
        return settings.SITE_URL + reverse("project_set", args=[self.uuid.hex])

    def __str__(self):
        return f"{self.project_set.title} - {self.uuid}"


class ProjectSetLinkAccess(models.Model):
    project_set = models.ForeignKey(ProjectSet, on_delete=models.CASCADE)
    ip_address_hash = models.CharField(max_length=255)
    accessed_at = models.DateTimeField(auto_now_add=True)


class EmailStatus(models.Model):
    email_id = models.CharField(max_length=255)
    recipient_email = models.EmailField()
    project_set = models.ForeignKey(ProjectSet, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    last_checked = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
