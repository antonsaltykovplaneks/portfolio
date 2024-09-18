import tablib
from django import forms
from django.contrib import admin, messages
from django.http import HttpResponse
from django.template.response import TemplateResponse
from elasticsearch.helpers import bulk
from import_export import fields, resources, widgets
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import CSV, TextFormat
from import_export.forms import ImportForm

from accounts.models import User
from infrastructure.elastic import ProjectDocument

from .models import Company, Industry, Project, ProjectSet, Technology


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


@admin.register(ProjectSet)
class ProjectSetAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_public",
        "created_at",
        "updated_at",
        "user",
    )
    list_filter = ("is_public", "created_at")
    search_fields = ("title",)
    filter_horizontal = ("projects",)


class ManyToManyCommaWidget(widgets.ManyToManyWidget):
    def __init__(self, model, field="title", separator=","):
        super().__init__(model, field=field, separator=separator)

    def clean(self, value, row=None, *args, **kwargs):
        if isinstance(value, str):
            return [item.strip() for item in value.split(self.separator)]
        return value


class ProjectResource(resources.ModelResource):
    user_id = fields.Field(
        column_name="user_id",
        attribute="user",
        widget=widgets.ForeignKeyWidget(User, "id"),
        default=None,
    )

    industries = fields.Field(
        attribute="industries",
        widget=ManyToManyCommaWidget(Industry, field="title"),
    )
    technologies = fields.Field(
        attribute="technologies",
        widget=ManyToManyCommaWidget(Technology, field="title"),
    )

    class Meta:
        model = Project
        fields = (
            "user_id",
            "title",
            "description",
            "url",
            "industries",
            "technologies",
        )

    def get_import_id_fields(self):
        return ["user_id", "title"]

    def before_import(self, dataset, **kwargs):
        super().before_import(dataset, **kwargs)
        # Append a column for user_id with the value proviai[ded in kwargs
        # Avoids Dimension Error
        dataset.append_col(
            [kwargs.get("user_id")] * dataset.__len__(), header="user_id"
        )

    def before_import_row(self, row, row_number=None, **kwargs):
        # Process technologies field: split by comma and get or create Technology objects
        technologies = row.get("technologies")
        tech_ids = list()
        if technologies:
            for tech in technologies.split(","):
                tech_obj = Technology.objects.filter(title__iexact=tech.lower()).first()
                if not tech_obj:
                    tech_obj = Technology.objects.create(title=tech)
                tech_ids.append(tech_obj.id)
            row["technologies"] = tech_ids

        # Process industries field: split by comma and get or create Industry objects
        industries = row.get("industries")
        industry_ids = list()
        if industries:
            for industry in industries.split(","):
                industry_obj = Industry.objects.filter(
                    title__iexact=industry.lower()
                ).first()
                if not industry_obj:
                    industry_obj = Industry.objects.create(title=industry)
                industry_ids.append(industry_obj.id)
            row["industries"] = industry_ids

        # Set user_id in the row if provided in kwargs
        user_id = kwargs.get("user_id")
        if user_id:
            row["user_id"] = user_id

    def after_init_instance(self, instance, new, row, **kwargs):
        # Set user_id on the instance if provided in the row
        user_id = row.get("user_id")
        if user_id:
            instance.user_id = user_id


class ProjectResourceExport(ProjectResource):
    class Meta:
        model = Project
        fields = (
            "title",
            "description",
            "url",
            "industries",
            "technologies",
        )

        export_order = (
            "title",
            "description",
            "url",
            "industries",
            "technologies",
        )


class UserSelectForm(ImportForm):
    # Custom form to select a user during import
    user = forms.ModelChoiceField(
        queryset=User.objects.all(), required=False, label="Select User"
    )


class UserExportForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(), required=False, label="Select User"
    )


class SemicolonCSV(TextFormat):
    # Custom CSV format with semicolon delimiter
    TABLIB_MODULE = "tablib.formats._csv"
    CONTENT_TYPE = "text/csv"

    def create_dataset(self, in_stream, **kwargs):
        # Create dataset from input stream with semicolon delimiter
        dataset = super().create_dataset(in_stream, **kwargs)
        dataset = tablib.Dataset().load(in_stream, format="csv", delimiter=";")
        return dataset

    def export_data(self, dataset, **kwargs):
        return dataset.export("csv", delimiter=";")


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    resource_class = ProjectResource
    list_display = ("title", "created_at", "updated_at", "user")
    list_filter = ("created_at", "updated_at", "user")
    search_fields = ("title", "description")
    ordering = ("title",)
    filter_horizontal = ("industries", "technologies")
    readonly_fields = ("created_at", "updated_at")

    def get_export_formats(self):
        # Override export formats to use SemicolonCSV instead of default CSV
        formats = super().get_export_formats()
        for i, format_class in enumerate(formats):
            if format_class is CSV:
                formats[i] = SemicolonCSV
        return formats

    def get_import_formats(self):
        # Override import formats to use SemicolonCSV instead of default CSV
        formats = super().get_import_formats()
        for i, format_class in enumerate(formats):
            if format_class is CSV:
                formats[i] = SemicolonCSV
        return formats

    def import_action(self, request, *args, **kwargs):
        user_form = UserSelectForm(formats=[CSV], resources=[ProjectResource])

        if request.method == "POST":
            user_form = UserSelectForm(
                formats=[CSV],
                files=request.FILES,
                resources=[ProjectResource],
                data={"user": request.POST.get("user"), "format": "0"},
            )

            if user_form.is_valid():
                file = request.FILES["import_file"]
                data = file.read().decode("utf-8")

                dataset = self.get_import_formats()[0]().create_dataset(
                    data, delimiter=";"
                )
                # Process the dataset with the selected user_id
                result = self.process_dataset(
                    dataset,
                    request=request,
                    form=user_form,
                    user_id=user_form.cleaned_data["user"].id,
                    *args,
                    **kwargs,
                )
                print(f"Result: {result.totals}")
                if not result.has_errors() and not result.has_validation_errors():
                    created_or_updated_ids = set()
                    for row_result in result.rows:
                        if row_result.import_type in ("new", "update"):
                            created_or_updated_ids.add(row_result.object_id)

                    # Bulk indexing of only newly created or updated projects
                    projects_to_index = Project.objects.filter(
                        id__in=created_or_updated_ids
                    )
                    actions = (
                        ProjectDocument.get_indexing_action(project)
                        for project in projects_to_index
                    )
                    index_result = bulk(ProjectDocument._get_connection(), actions)
                    print(f"Indexing Result: {index_result}")
                    messages.success(request, "Import successful!")
                    return self.process_result(result, request)
                else:
                    messages.error(request, "Import failed due to errors.")

        context = self.get_import_context_data(**kwargs)
        context["form"] = user_form
        return TemplateResponse(request, self.import_template_name, context)

    def get_import_context_data(self, **kwargs):
        # Add model metadata to the context
        context = super().get_import_context_data(**kwargs)
        context["opts"] = self.model._meta
        return context

    def export_action(self, request, *args, **kwargs):
        if request.method == "POST":
            form = UserExportForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data["user"]
                queryset = self.get_queryset(request)
                if user:
                    queryset = queryset.filter(user=user)
                export_data = self.get_export_data(request, queryset, *args, **kwargs)
                content_type = self.get_export_formats()[0].CONTENT_TYPE
                response = HttpResponse(export_data, content_type=content_type)
                response["Content-Disposition"] = f'attachment; filename="projects.csv"'
                return response
        else:
            form = UserExportForm()

        context = {
            "form": form,
            "opts": self.model._meta,
            "action_checkbox_name": admin.helpers.ACTION_CHECKBOX_NAME,
        }

        return TemplateResponse(request, self.import_template_name, context)

    def get_export_data(self, request, queryset, *args, **kwargs):
        export_format = self.get_export_formats()[0]()

        export_data = export_format.export_data(
            ProjectResourceExport().export(queryset=queryset),
            **kwargs,
        )

        return export_data
