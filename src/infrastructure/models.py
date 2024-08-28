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

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)

    industries = models.ManyToManyField("Industry", related_name="projects")
    technologies = models.ManyToManyField("Technology", related_name="projects")

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
