from django import forms
from .models import Resume, PersonalInfo


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ["title"]

class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = PersonalInfo
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "city",
            "about",
            "photo",
        ]