from django import forms
from .models import Resume, PersonalInfo, Education, WorkExperience, Skill


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
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
        }

class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = [
            "company",
            "position",
            "start_date",
            "end_date",
            "description",
        ]

        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = [
            "name",
            "level",
        ]