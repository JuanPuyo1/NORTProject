from django.contrib import admin

from .models import CollaborationInquiry


@admin.register(CollaborationInquiry)
class CollaborationInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "role", "created_at", "is_read")
    list_filter = ("role", "is_read", "created_at")
    search_fields = ("name", "email", "organization", "message")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
