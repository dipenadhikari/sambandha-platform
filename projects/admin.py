from django.contrib import admin

from .models import Activity, Estimate, Lead, Project


class EstimateInline(admin.StackedInline):
    model = Estimate
    extra = 0
    readonly_fields = (
        "selections",
        "subtotal",
        "coordination_fee",
        "location_adjustment",
        "estimate_low",
        "estimate_high",
        "pricing_version",
        "created_at",
    )


class ProjectInline(admin.StackedInline):
    model = Project
    extra = 0


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "location", "finish_level", "created_at")
    search_fields = ("full_name", "phone", "email", "location")
    list_filter = ("project_type", "finish_level", "created_at")
    inlines = (EstimateInline, ProjectInline)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("lead", "status", "assigned_to", "site_visit_at", "updated_at")
    list_filter = ("status", "assigned_to")
    search_fields = ("lead__full_name", "lead__phone", "lead__location")


admin.site.register(Activity)

