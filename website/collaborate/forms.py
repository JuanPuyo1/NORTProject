from django import forms

from .models import CollaborationInquiry


class CollaborationForm(forms.ModelForm):
    class Meta:
        model = CollaborationInquiry
        fields = ["name", "email", "organization", "role", "message", "consent_given"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full rounded-xl h-12",
                    "placeholder": "Ada Lovelace",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "input input-bordered w-full rounded-xl h-12",
                    "placeholder": "you@lab.edu",
                }
            ),
            "organization": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full rounded-xl h-12",
                    "placeholder": "University, lab, or independent",
                }
            ),
            "role": forms.Select(attrs={"class": "select select-bordered w-full rounded-xl h-12"}),
            "message": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full rounded-xl min-h-[120px]",
                    "placeholder": "A few sentences. Links welcome.",
                    "rows": 5,
                }
            ),
            "consent_given": forms.CheckboxInput(
                attrs={"class": "checkbox checkbox-sm rounded border-base-300"}
            ),
        }

    def clean_consent_given(self):
        consent = self.cleaned_data.get("consent_given")
        if not consent:
            raise forms.ValidationError(
                "You must acknowledge this is research contact, not medical support."
            )
        return consent
