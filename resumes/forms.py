from django import forms
from .models import Resume, PersonalInfo, Education


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

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = [
            "institution",
            "specialty",
            "start_date",
            "end_date",
            "description",
        ]

        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }