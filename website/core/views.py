from django.shortcuts import render

from blog.models import BlogPost


def home(request):
    latest_posts = BlogPost.objects.filter(is_published=True)[:3]
    return render(request, "core/home.html", {"latest_posts": latest_posts})
