import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse


class Lead(models.Model):
    class ProjectType(models.TextChoices):
        INTERIOR = "interior", "Interior"
        EXTERIOR = "exterior", "Exterior"
        BOTH = "both", "Interior and exterior"
        COMMERCIAL = "commercial", "Commercial space"

    class FinishLevel(models.TextChoices):
        BASIC = "basic", "Basic"
        MEDIUM = "medium", "Medium"
        PREMIUM = "premium", "Premium"

    reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    full_name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30)
    location = models.CharField(max_length=160)
    project_type = models.CharField(max_length=20, choices=ProjectType.choices)
    finish_level = models.CharField(max_length=20, choices=FinishLevel.choices)
    desired_start = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    consent_to_contact = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.location}"


class Estimate(models.Model):
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name="estimate")
    selections = models.JSONField(default=list)
    subtotal = models.PositiveBigIntegerField()
    coordination_fee = models.PositiveBigIntegerField()
    location_adjustment = models.IntegerField(default=0)
    estimate_low = models.PositiveBigIntegerField()
    estimate_high = models.PositiveBigIntegerField()
    pricing_version = models.CharField(max_length=30, default="2026.09")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Estimate {self.lead.reference}"


class Project(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New inquiry"
        CONTACTED = "contacted", "Contacted"
        SITE_VISIT = "site_visit", "Site visit scheduled"
        PROPOSAL = "proposal", "Proposal sent"
        WON = "won", "Approved"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        LOST = "lost", "Not proceeding"

    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name="project")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="assigned_projects",
    )
    site_visit_at = models.DateTimeField(blank=True, null=True)
    next_action = models.CharField(max_length=240, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.lead.full_name} — {self.get_status_display()}"

    def get_absolute_url(self):
        return reverse("staff_project_detail", kwargs={"pk": self.pk})


class Activity(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="activities")
    event = models.CharField(max_length=80)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="project_activities",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "activities"

    def __str__(self):
        return f"{self.project_id}: {self.event}"

