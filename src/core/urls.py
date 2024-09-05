from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("csv-upload/", views.upload_csv, name="upload_csv"),
]
