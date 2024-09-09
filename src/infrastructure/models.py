from django.db import models


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

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)

    industries = models.ManyToManyField("Industry", related_name="projects")
    technologies = models.ManyToManyField("Technology", related_name="projects")

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

    def __str__(self):
        return self.title
