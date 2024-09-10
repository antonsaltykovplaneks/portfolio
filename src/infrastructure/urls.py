from django.urls import path
from . import views


urlpatterns = [
    path(
        "sets/<int:project_set_id>/",
        views.ProjectSetDetailView.as_view(),
        name="get_project_set",
    ),
    path("sets/", views.ProjectSetView.as_view(), name="project_set"),
    path("projects/<int:project_id>/", views.ProjectView.as_view(), name="project"),
    path("industries/", views.IndustryListView.as_view(), name="industry-list"),
    path("technologies/", views.TechnologyListView.as_view(), name="technology-list"),
]
