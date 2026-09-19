from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.blog_list, name="list"),
    path("partials/home/", views.blog_partials_home, name="partials_home"),
    path("<slug:slug>/", views.blog_detail, name="detail"),
]
