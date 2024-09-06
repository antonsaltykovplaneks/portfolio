from django.urls import path
from . import views


urlpatterns = [
    path(
        "sets/<int:project_set_id>/",
        views.ProjectSetDetailView.as_view(),
        name="get_project_set",
    ),
    path("sets/", views.ProjectSetView.as_view(), name="project_set"),
]
