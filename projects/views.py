from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ActivityForm, ProjectUpdateForm, QuoteRequestForm
from .models import Activity, Estimate, Lead, Project
from .pricing import PricingError, SERVICES, calculate_estimate


def home(request):
    return render(request, "projects/home.html")


@transaction.atomic
def quote_request(request):
    form = QuoteRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            result = calculate_estimate(form.cleaned_data["finish_level"], form.quantities())
        except PricingError as exc:
            form.add_error(None, str(exc))
        else:
            lead = form.save()
            Estimate.objects.create(
                lead=lead,
                selections=result["line_items"],
                subtotal=result["subtotal"],
                coordination_fee=result["coordination_fee"],
                location_adjustment=result["location_adjustment"],
                estimate_low=result["estimate_low"],
                estimate_high=result["estimate_high"],
            )
            project = Project.objects.create(
                lead=lead,
                next_action="Contact the customer within one business day.",
            )
            Activity.objects.create(project=project, event="Inquiry submitted")
            return redirect("quote_success", reference=lead.reference)

    return render(
        request,
        "projects/quote_form.html",
        {"form": form, "services": SERVICES},
    )


def quote_success(request, reference):
    lead = get_object_or_404(Lead.objects.select_related("estimate"), reference=reference)
    return render(request, "projects/quote_success.html", {"lead": lead})


def _staff_check(user):
    return user.is_active and user.is_staff


@login_required
@user_passes_test(_staff_check)
def staff_dashboard(request):
    status = request.GET.get("status", "")
    query = request.GET.get("q", "").strip()
    projects = Project.objects.select_related("lead", "lead__estimate", "assigned_to")
    if status in Project.Status.values:
        projects = projects.filter(status=status)
    if query:
        projects = projects.filter(
            Q(lead__full_name__icontains=query)
            | Q(lead__phone__icontains=query)
            | Q(lead__location__icontains=query)
        )
    counts = dict(
        Project.objects.values_list("status")
        .annotate(total=Count("id"))
        .values_list("status", "total")
    )
    status_cards = [
        {"value": value, "label": label, "count": counts.get(value, 0)}
        for value, label in Project.Status.choices
    ]
    return render(
        request,
        "projects/staff_dashboard.html",
        {"projects": projects, "status_cards": status_cards, "active_status": status, "query": query},
    )


@login_required
@user_passes_test(_staff_check)
@transaction.atomic
def staff_project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("lead", "lead__estimate", "assigned_to").prefetch_related(
            "activities__created_by"
        ),
        pk=pk,
    )
    update_form = ProjectUpdateForm(instance=project, prefix="project")
    activity_form = ActivityForm(prefix="activity")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update":
            previous_status = project.status
            update_form = ProjectUpdateForm(request.POST, instance=project, prefix="project")
            if update_form.is_valid():
                project = update_form.save()
                event = "Project details updated"
                if previous_status != project.status:
                    event = f"Status changed to {project.get_status_display()}"
                Activity.objects.create(project=project, event=event, created_by=request.user)
                messages.success(request, "Project updated.")
                return redirect(project)
        elif action == "note":
            activity_form = ActivityForm(request.POST, prefix="activity")
            if activity_form.is_valid():
                activity = activity_form.save(commit=False)
                activity.project = project
                activity.event = "Staff note"
                activity.created_by = request.user
                activity.save()
                messages.success(request, "Note added.")
                return redirect(project)

    return render(
        request,
        "projects/staff_project_detail.html",
        {"project": project, "update_form": update_form, "activity_form": activity_form},
    )

