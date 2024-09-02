from django.urls import path
from . import views


urlpatterns = [
    path("projects/", views.project_search_view, name="projects"),
]
