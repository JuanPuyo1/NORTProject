from django.urls import path

from . import views

app_name = "collaborate"

urlpatterns = [
    path("", views.collaborate, name="index"),
    path("success/", views.collaborate_success, name="success"),
]
