from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import CollaborationForm


def collaborate(request):
    form = CollaborationForm()
    if request.method == "POST":
        form = CollaborationForm(request.POST)
        if form.is_valid():
            form.save()
            if request.htmx:
                return render(request, "collaborate/partials/success.html")
            return redirect(reverse("collaborate:success"))

    return render(request, "collaborate/index.html", {"form": form})


def collaborate_success(request):
    return render(request, "collaborate/success.html")
