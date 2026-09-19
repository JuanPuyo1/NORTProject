from django.db import models


class CollaborationInquiry(models.Model):
    class Role(models.TextChoices):
        RESEARCHER = "researcher", "Researcher"
        ENGINEER = "engineer", "Engineer"
        CLINICIAN = "clinician", "Clinician"
        STUDENT = "student", "Student"
        OTHER = "other", "Other"

    name = models.CharField(max_length=120)
    email = models.EmailField()
    organization = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.RESEARCHER)
    message = models.TextField()
    consent_given = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "collaboration inquiries"

    def __str__(self):
        return f"{self.name} ({self.email})"
