from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Activity, Estimate, Lead, Project
from .pricing import PricingError, calculate_estimate


class PricingTests(TestCase):
    def test_calculates_medium_estimate_from_server_prices(self):
        result = calculate_estimate(
            "medium",
            {"modular_kitchen": 1, "interior_painting": 1_000},
        )
        self.assertEqual(result["subtotal"], 895_000)
        self.assertEqual(result["coordination_fee"], 53_700)
        self.assertEqual(result["estimate_low"], 853_830)
        self.assertEqual(result["estimate_high"], 1_062_544)
        self.assertEqual(len(result["line_items"]), 2)

    def test_rejects_empty_selection(self):
        with self.assertRaises(PricingError):
            calculate_estimate("basic", {"modular_kitchen": 0})

    def test_rejects_quantity_above_service_limit(self):
        with self.assertRaises(PricingError):
            calculate_estimate("premium", {"bathroom_upgrade": 11})


class QuoteWorkflowTests(TestCase):
    def valid_payload(self):
        return {
            "full_name": "Test Customer",
            "phone": "+977-9800000099",
            "email": "customer@example.com",
            "location": "Kathmandu",
            "project_type": "interior",
            "finish_level": "medium",
            "desired_start": "2026-11-01",
            "notes": "Please call in the afternoon.",
            "consent_to_contact": "on",
            "service_modular_kitchen": "1",
            "service_interior_painting": "1000",
        }

    def test_submission_creates_connected_business_records(self):
        response = self.client.post(reverse("quote_request"), self.valid_payload())
        lead = Lead.objects.get()
        self.assertRedirects(response, reverse("quote_success", args=[lead.reference]))
        self.assertTrue(Estimate.objects.filter(lead=lead).exists())
        project = Project.objects.get(lead=lead)
        self.assertEqual(project.status, Project.Status.NEW)
        self.assertEqual(project.activities.first().event, "Inquiry submitted")

    def test_submission_requires_at_least_one_service(self):
        payload = self.valid_payload()
        payload["service_modular_kitchen"] = "0"
        payload["service_interior_painting"] = "0"
        response = self.client.post(reverse("quote_request"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select at least one service")
        self.assertEqual(Lead.objects.count(), 0)


class StaffWorkflowTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff = User.objects.create_user(
            username="staff", password="safe-password-123", is_staff=True
        )
        self.non_staff = User.objects.create_user(username="customer", password="safe-password-123")
        self.lead = Lead.objects.create(
            full_name="Pipeline Customer",
            phone="9800000000",
            location="Kathmandu",
            project_type=Lead.ProjectType.INTERIOR,
            finish_level=Lead.FinishLevel.BASIC,
            consent_to_contact=True,
        )
        result = calculate_estimate("basic", {"modular_kitchen": 1})
        Estimate.objects.create(
            lead=self.lead,
            selections=result["line_items"],
            subtotal=result["subtotal"],
            coordination_fee=result["coordination_fee"],
            estimate_low=result["estimate_low"],
            estimate_high=result["estimate_high"],
        )
        self.project = Project.objects.create(lead=self.lead)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("staff_dashboard"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('staff_dashboard')}",
        )

    def test_non_staff_user_cannot_open_dashboard(self):
        self.client.login(username="customer", password="safe-password-123")
        response = self.client.get(reverse("staff_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_staff_can_change_status_and_audit_event_is_created(self):
        self.client.login(username="staff", password="safe-password-123")
        response = self.client.post(
            reverse("staff_project_detail", args=[self.project.pk]),
            {
                "action": "update",
                "project-status": Project.Status.CONTACTED,
                "project-assigned_to": str(self.staff.pk),
                "project-site_visit_at": "",
                "project-next_action": "Schedule a site visit.",
            },
        )
        self.assertRedirects(response, self.project.get_absolute_url())
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.Status.CONTACTED)
        self.assertTrue(
            Activity.objects.filter(project=self.project, event__contains="Contacted").exists()
        )

