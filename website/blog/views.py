from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from markdown import markdown

from .models import BlogPost

POSTS_PER_PAGE = 4


def _published_posts(category=None):
    queryset = BlogPost.objects.filter(is_published=True, published_at__lte=timezone.now())
    if category and category != "all":
        queryset = queryset.filter(category=category)
    return queryset


def blog_list(request):
    category = request.GET.get("category", "all")
    page_number = request.GET.get("page", 1)
    posts = _published_posts(category)
    featured = posts.filter(is_featured=True).first()
    list_posts = posts.exclude(pk=featured.pk if featured else None)

    paginator = Paginator(list_posts, POSTS_PER_PAGE)
    page = paginator.get_page(page_number)

    context = {
        "category": category,
        "featured_post": featured,
        "page": page,
        "categories": BlogPost.Category.choices,
        "has_more": page.has_next(),
        "next_page": page.next_page_number() if page.has_next() else None,
    }

    partial = request.GET.get("partial")
    if request.htmx and partial == "posts":
        return render(request, "blog/partials/post_list.html", context)
    if request.htmx and partial == "rows":
        return render(request, "blog/partials/post_rows.html", context)

    return render(request, "blog/list.html", context)


def blog_detail(request, slug):
    post = get_object_or_404(
        BlogPost,
        slug=slug,
        is_published=True,
        published_at__lte=timezone.now(),
    )
    content_html = markdown(
        post.content,
        extensions=["extra", "nl2br", "sane_lists"],
    )
    return render(
        request,
        "blog/detail.html",
        {"post": post, "content_html": content_html},
    )


def blog_partials_home(request):
    posts = BlogPost.objects.filter(is_published=True)[:3]
    return render(request, "blog/partials/home_cards.html", {"posts": posts})
