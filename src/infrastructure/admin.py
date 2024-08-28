from django.contrib import admin

from .forms import (
    CompanyCreateForm,
    CompanyEditForm,
    IndustryCreateForm,
    IndustryEditForm,
    ProjectCreateForm,
    ProjectEditForm,
    TechnologyCreateForm,
    TechnologyEditForm,
)
from .models import Company, Industry, Project, Technology


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)

    add_fieldsets = ((None, {"fields": ("title",)}),)
    list_display = ("title",)
    list_filter = ("title",)
    ordering = ("title",)

    form = CompanyEditForm
    add_form = CompanyCreateForm


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)

    add_fieldsets = ((None, {"fields": ("title",)}),)
    list_display = ("title",)
    list_filter = ("title",)
    ordering = ("title",)

    form = IndustryEditForm
    add_form = IndustryCreateForm


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)

    add_fieldsets = ((None, {"fields": ("title",)}),)
    list_display = ("title",)
    list_filter = ("title",)
    ordering = ("title",)

    form = TechnologyEditForm
    add_form = TechnologyCreateForm


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "updated_at", "user")
    list_filter = ("title", "created_at", "updated_at", "user")
    search_fields = ("title", "description")
    ordering = ("title",)
    filter_horizontal = ("industries", "technologies")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "description",
                    "image",
                    "user",
                    "industries",
                    "technologies",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    readonly_fields = ("created_at", "updated_at")
    form = ProjectEditForm
    add_form = ProjectCreateForm
