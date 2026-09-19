from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class BlogPost(models.Model):
    class Category(models.TextChoices):
        SOFTWARE = "software", "Software"
        HARDWARE = "hardware", "Hardware"
        METHODS = "methods", "Methods"
        STATUS = "status", "Status"

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    excerpt = models.TextField(help_text="Short summary shown on cards and list views.")
    content = models.TextField(help_text="Full lab note body. Markdown supported.")
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.SOFTWARE,
    )
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured post shown in the highlighted card on the blog page.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

    @property
    def category_label(self):
        return self.get_category_display()
