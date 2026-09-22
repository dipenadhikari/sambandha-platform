from django import forms

from .models import Activity, Lead, Project
from .pricing import SERVICES


class QuoteRequestForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            "full_name",
            "phone",
            "email",
            "location",
            "project_type",
            "finish_level",
            "desired_start",
            "notes",
            "consent_to_contact",
        ]
        widgets = {
            "desired_start": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for service in SERVICES:
            self.fields[f"service_{service.key}"] = forms.IntegerField(
                label=f"{service.name} ({service.unit})",
                min_value=0,
                max_value=service.max_quantity,
                required=False,
                initial=0,
                widget=forms.NumberInput(
                    attrs={
                        "data-service": service.key,
                        "data-basic": service.prices["basic"],
                        "data-medium": service.prices["medium"],
                        "data-premium": service.prices["premium"],
                        "inputmode": "numeric",
                    }
                ),
            )

    def clean_consent_to_contact(self):
        value = self.cleaned_data["consent_to_contact"]
        if not value:
            raise forms.ValidationError("Please confirm that Sambandha may contact you.")
        return value

    def quantities(self):
        return {
            service.key: self.cleaned_data.get(f"service_{service.key}") or 0
            for service in SERVICES
        }


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["status", "assigned_to", "site_visit_at", "next_action"]
        widgets = {
            "site_visit_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = self.fields["assigned_to"].queryset.filter(
            is_staff=True
        )


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["note"]
        widgets = {"note": forms.Textarea(attrs={"rows": 3, "placeholder": "Call notes, client decision, or next step"})}

