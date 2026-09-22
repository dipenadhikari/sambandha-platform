from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from projects.models import Activity, Estimate, Lead, Project
from projects.pricing import calculate_estimate


DEMO_PROJECTS = (
    {
        "full_name": "Aarav Shrestha",
        "phone": "+977-9800000001",
        "email": "aarav@example.com",
        "location": "Baneshwor, Kathmandu",
        "project_type": Lead.ProjectType.INTERIOR,
        "finish_level": Lead.FinishLevel.MEDIUM,
        "status": Project.Status.CONTACTED,
        "quantities": {"modular_kitchen": 1, "false_ceiling": 700, "interior_painting": 1400},
        "next_action": "Confirm a measurement visit for Saturday.",
    },
    {
        "full_name": "Maya Gurung",
        "phone": "+977-9800000002",
        "email": "maya@example.com",
        "location": "Lalitpur",
        "project_type": Lead.ProjectType.BOTH,
        "finish_level": Lead.FinishLevel.PREMIUM,
        "status": Project.Status.SITE_VISIT,
        "quantities": {"living_tv_wall": 1, "flooring": 1200, "exterior_painting": 1600},
        "next_action": "Prepare the material brief after the site visit.",
    },
    {
        "full_name": "Kiran Rai",
        "phone": "+977-9800000003",
        "email": "",
        "location": "Bhaktapur",
        "project_type": Lead.ProjectType.EXTERIOR,
        "finish_level": Lead.FinishLevel.BASIC,
        "status": Project.Status.NEW,
        "quantities": {"waterproofing": 900, "boundary_gate": 1},
        "next_action": "Call to understand the waterproofing condition.",
    },
)


class Command(BaseCommand):
    help = "Create an explainable staff account and sample project records."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="demo_staff")
        parser.add_argument("--password", default="ChangeMe123!")

    def handle(self, *args, **options):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=options["username"],
            defaults={"is_staff": True, "is_active": True},
        )
        if created:
            user.set_password(options["password"])
            user.save()

        created_count = 0
        for index, item in enumerate(DEMO_PROJECTS):
            lead, lead_created = Lead.objects.get_or_create(
                phone=item["phone"],
                defaults={
                    "full_name": item["full_name"],
                    "email": item["email"],
                    "location": item["location"],
                    "project_type": item["project_type"],
                    "finish_level": item["finish_level"],
                    "consent_to_contact": True,
                },
            )
            if not lead_created:
                continue
            result = calculate_estimate(item["finish_level"], item["quantities"])
            Estimate.objects.create(
                lead=lead,
                selections=result["line_items"],
                subtotal=result["subtotal"],
                coordination_fee=result["coordination_fee"],
                estimate_low=result["estimate_low"],
                estimate_high=result["estimate_high"],
            )
            project = Project.objects.create(
                lead=lead,
                status=item["status"],
                assigned_to=user if index < 2 else None,
                site_visit_at=timezone.now() + timedelta(days=3) if index == 1 else None,
                next_action=item["next_action"],
            )
            Activity.objects.create(
                project=project,
                event="Demo inquiry created",
                note="Sample record for local development only.",
                created_by=user,
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_count} demo projects."))
        if created:
            self.stdout.write(
                f"Staff login: {options['username']} / {options['password']} (change it immediately)"
            )
        else:
            self.stdout.write("Existing staff password was not changed.")

