"""
Seed or update public lab notes from version-controlled definitions.

Release flow (after an achievement on main):
1. Merge main into prod.
2. Add a new dict to POSTS below (unique slug, is_published via seed defaults).
3. Push prod → GitHub Actions builds the image → VPS pulls and restarts.
4. entrypoint runs seed_blog_posts on every container start (idempotent).
"""

from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import BlogPost


POSTS = [
    {
        "title": "Iteration analysis after the classical ladder",
        "slug": "iteration-analysis-classical-ladder",
        "category": BlogPost.Category.STATUS,
        "published_at": datetime(2026, 8, 4, 12, 0),
        "is_featured": True,
        "excerpt": "What held up across CSP, FBCSP, Riemannian, and SVD runs — and what did not transfer.",
        "content": """## Summary

A read-through of CSP, FBCSP, Riemannian tangent-space LDA, truncated SVD+SVM, and EEGNet on the Nieto Inner Speech set.

## What transferred

Subject-wise splits stayed honest. The classical ladder ran end-to-end with logged configs.

## What collapsed

Leave-session-out accuracies stayed near chance across the board. No recipe on scalp EEG alone cleared a decoder go/no-go.

## Next gate

Controls, alternate data, and different feature assumptions before hardware integration.""",
    },
    {
        "title": "EEGNet on Inner Speech derivatives",
        "slug": "eegnet-inner-speech-derivatives",
        "category": BlogPost.Category.SOFTWARE,
        "published_at": datetime(2026, 7, 21, 12, 0),
        "excerpt": "First deep baseline with the same subject-wise splits used by the classical stack.",
        "content": """First deep baseline using the same subject-wise and session-wise splits as the classical stack.

EEGNet trained on preprocessed derivatives with identical evaluation protocol. Results logged alongside CSP and Riemannian runs.""",
    },
    {
        "title": "Classical ladder final report",
        "slug": "classical-ladder-final-report",
        "category": BlogPost.Category.METHODS,
        "published_at": datetime(2026, 7, 20, 18, 0),
        "excerpt": "CSP+LDA, FBCSP findings, Riemannian TS+LDA, and truncated SVD+SVM in one comparison.",
        "content": """Logged accuracies and the decision trail for the Phase 0 decoding backbone.

Methods compared under leave-session-out evaluation on inner speech trials.""",
    },
    {
        "title": "5 GB multi-subject Inner Speech load",
        "slug": "5gb-multi-subject-inner-speech-load",
        "category": BlogPost.Category.SOFTWARE,
        "published_at": datetime(2026, 7, 20, 14, 0),
        "excerpt": "Capped derivative download and the first end-to-end training script that other people can rerun.",
        "content": """Capped derivative download from OpenNeuro ds003626 and the first reproducible training script for the Phase 0 stack.""",
    },
    {
        "title": "Why TribeV2 is deferred",
        "slug": "why-tribev2-is-deferred",
        "category": BlogPost.Category.METHODS,
        "published_at": datetime(2026, 7, 20, 10, 0),
        "excerpt": "Useful later, not the Phase 0 backbone. Decision logged with the dataset assessment.",
        "content": """TribeV2 remains on the assessment list. Phase 0 stays on Nieto Inner Speech until signal and protocol questions are settled.""",
    },
]


class Command(BaseCommand):
    help = "Seed initial lab notes for the NORT website."

    def handle(self, *args, **options):
        created = 0
        for data in POSTS:
            if data.get("is_featured"):
                BlogPost.objects.exclude(slug=data["slug"]).update(is_featured=False)

            published_at = timezone.make_aware(data["published_at"])
            post, was_created = BlogPost.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    **data,
                    "published_at": published_at,
                    "is_published": True,
                },
            )
            if was_created:
                created += 1
            self.stdout.write(f"{'Created' if was_created else 'Updated'}: {post.title}")

        self.stdout.write(self.style.SUCCESS(f"Done. {created} new posts."))
