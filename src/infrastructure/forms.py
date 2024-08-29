from typing import Any

from django import forms

from .models import Company, Industry, Project, Technology


class CompanyEditForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = "__all__"

    def save(self, commit: bool = True) -> Any:
        return super().save(commit)


class CompanyCreateForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = "__all__"


class IndustryEditForm(forms.ModelForm):
    class Meta:
        model = Industry
        fields = "__all__"


class IndustryCreateForm(forms.ModelForm):
    class Meta:
        model = Industry
        fields = "__all__"


class TechnologyEditForm(forms.ModelForm):
    class Meta:
        model = Technology
        fields = "__all__"


class TechnologyCreateForm(forms.ModelForm):
    class Meta:
        model = Technology
        fields = "__all__"


class ProjectEditForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
