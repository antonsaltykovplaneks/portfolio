from django.contrib import admin

from .models import Company, Industry, Project, Technology


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)

    add_fieldsets = ((None, {"fields": ("title",)}),)
    list_display = ("title",)
    list_filter = ("title",)
    ordering = ("title",)


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)

    add_fieldsets = ((None, {"fields": ("title",)}),)
    list_display = ("title",)
    list_filter = ("title",)
    ordering = ("title",)


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)

    add_fieldsets = ((None, {"fields": ("title",)}),)
    list_display = ("title",)
    list_filter = ("title",)
    ordering = ("title",)


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
