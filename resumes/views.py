from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from django.conf import settings
from pathlib import Path
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.db import transaction

from .models import Resume, PersonalInfo, Education, WorkExperience, Skill
from .forms import ResumeForm, PersonalInfoForm, EducationForm, WorkExperienceForm, SkillForm

# Create your views here.

@login_required
def resume_list(request):
    resumes = Resume.objects.filter(owner=request.user)

    return render(request, "resumes/resume_list.html", {
        "resumes": resumes
    })

class ResumeCreateView(LoginRequiredMixin, CreateView):
    model = Resume
    form_class = ResumeForm
    template_name = "resumes/resume_create.html"
    success_url = reverse_lazy("resume_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ResumePDFView(LoginRequiredMixin, DetailView):
    model = Resume

    def get_queryset(self):
        return Resume.objects.filter(owner=self.request.user)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        personal_info = getattr(self.object, "personal_info", None)
        photo_url = None
        if personal_info and personal_info.photo:
            photo_url = Path(personal_info.photo.path).as_uri()

        templates = {
            "sidebar": "resumes/resume_pdf.html",
            "classic": "resumes/resume_pdf_classic.html",
            "modern": "resumes/resume_pdf_classic.html",
        }

        template_name = templates.get(
            self.object.template,
            templates["sidebar"],
        )

        stylesheets = {
            "sidebar": "static/css/resume_pdf.css",
            "classic": "static/css/resume_pdf_classic.css",
            "modern": "static/css/resume_pdf_modern.css",
        }
        stylesheet = stylesheets.get(self.object.template, stylesheets["sidebar"])

        html_string = render_to_string(
            template_name,
            {"resume": self.object, "photo_url": photo_url}
        )

        pdf = HTML(
            string=html_string,
            base_url=request.build_absolute_uri("/")
        ).write_pdf(stylesheets=[CSS(filename=str(settings.BASE_DIR / stylesheet))])

        response = HttpResponse(
            pdf,
            content_type="application/pdf"
        )

        preview = request.GET.get("preview") == "1"
        disposition = "inline" if preview else "attachment"

        response["Content-Disposition"] = (
            f'{disposition}; filename="{self.object.title}.pdf"'
        )

        return response

class ResumeDetailView(LoginRequiredMixin, DetailView):
    model = Resume
    template_name = "resumes/resume_detail.html"

    def get_queryset(self):
        return Resume.objects.filter(owner=self.request.user)

class ResumeUpdateView(LoginRequiredMixin, UpdateView):
    model = Resume
    fields = ["title", "template"]
    template_name = "resumes/resume_update.html"

    def get_queryset(self):
        return Resume.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse("resume_detail", kwargs={"pk": self.object.pk})

class ResumeDeleteView(LoginRequiredMixin, DeleteView):
    model = Resume
    template_name = "resumes/resume_confirm_delete.html"
    success_url = reverse_lazy("resume_list")

    def get_queryset(self):
        return Resume.objects.filter(owner=self.request.user)

class PersonalInfoCreateView(LoginRequiredMixin, CreateView):
    model = PersonalInfo
    form_class = PersonalInfoForm
    template_name = "resumes/personal_info_form.html"

    def form_valid(self, form):
        resume = Resume.objects.get(
            pk=self.kwargs["pk"],
            owner=self.request.user
        )

        form.instance.resume = resume

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("resume_detail", kwargs={"pk": self.object.resume.pk})

class EducationCreateView(LoginRequiredMixin, CreateView):
    model = Education
    form_class = EducationForm
    template_name = "resumes/education_form.html"

    def form_valid(self, form):
        resume = Resume.objects.get(
            pk=self.kwargs["pk"],
            owner=self.request.user
        )

        form.instance.resume = resume

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("resume_detail", kwargs={"pk": self.object.resume.pk})

class WorkExperienceCreateView(LoginRequiredMixin, CreateView):
    model = WorkExperience
    form_class = WorkExperienceForm
    template_name = "resumes/workexperience_form.html"

    def form_valid(self, form):
        resume = Resume.objects.get(
            pk=self.kwargs["pk"],
            owner=self.request.user
        )

        form.instance.resume = resume

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("resume_detail", kwargs={"pk": self.object.resume.pk})

class SkillCreateView(LoginRequiredMixin, CreateView):
    model = Skill
    form_class = SkillForm
    template_name = "resumes/skill_form.html"

    def form_valid(self, form):
        resume = Resume.objects.get(
            pk=self.kwargs["pk"],
            owner=self.request.user
        )

        form.instance.resume = resume

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("resume_detail", kwargs={"pk": self.object.resume.pk})

class SkillUpdateView(LoginRequiredMixin, UpdateView):
    model = Skill
    form_class = SkillForm
    template_name = "resumes/skill_form.html"

    def get_queryset(self):
        return Skill.objects.filter(
            resume__owner = self.request.user
        )

    def get_success_url(self):
        return reverse(
            "resume_detail",
            kwargs={"pk": self.object.resume.pk}
        )

class SkillDeleteView(LoginRequiredMixin, DeleteView):
    model = Skill
    template_name = "resumes/skill_confirm_delete.html"

    def get_success_url(self):
        return reverse(
            "resume_detail",
            kwargs={"pk": self.object.resume.pk}
        )

    def get_queryset(self):
        return Skill.objects.filter(resume__owner=self.request.user)


class PersonalInfoUpdateView(LoginRequiredMixin, UpdateView):
    model = PersonalInfo
    form_class = PersonalInfoForm
    template_name = "resumes/personal_info_form.html"

    def get_queryset(self):
        return PersonalInfo.objects.filter(resume__owner=self.request.user)

    def get_success_url(self):
        return reverse("resume_detail", kwargs={"pk": self.object.resume.pk})


class PersonalInfoDeleteView(LoginRequiredMixin, DeleteView):
    model = PersonalInfo
    template_name = "resumes/personal_info_confirm_delete.html"

    def get_queryset(self):
        return PersonalInfo.objects.filter(resume__owner=self.request.user)

    def get_success_url(self):
        return reverse("resume_detail", kwargs={"pk": self.object.resume.pk})


class EducationUpdateView(LoginRequiredMixin, UpdateView):
    model = Education
    form_class = EducationForm
    template_name = "resumes/education_form.html"

    def get_queryset(self):
        return Education.objects.filter(resume__owner=self.request.user)

    def get_success_url(self):
        return reverse("resume_detail", kwargs={"pk": self.object.resume.pk})


class EducationDeleteView(LoginRequiredMixin, DeleteView):
    model = Education
    template_name = "resumes/education_confirm_delete.html"

    def get_queryset(self):
        return Education.objects.filter(resume__owner=self.request.user)

    def get_success_url(self):
        return reverse("resume_detail", kwargs={"pk": self.object.resume.pk})


class WorkExperienceUpdateView(LoginRequiredMixin, UpdateView):
    model = WorkExperience
    form_class = WorkExperienceForm
    template_name = "resumes/workexperience_form.html"

    def get_queryset(self):
        return WorkExperience.objects.filter(resume__owner=self.request.user)

    def get_success_url(self):
        return reverse("resume_detail", kwargs={"pk": self.object.resume.pk})


class WorkExperienceDeleteView(LoginRequiredMixin, DeleteView):
    model = WorkExperience
    template_name = "resumes/work_experience_confirm_delete.html"

    def get_queryset(self):
        return WorkExperience.objects.filter(resume__owner=self.request.user)

    def get_success_url(self):
        return reverse("resume_detail", kwargs={"pk": self.object.resume.pk})

class ResumeCloneView(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, pk):
        original = get_object_or_404(
            Resume,
            pk=pk,
            owner=request.user,
        )

        suffix = " — копія"
        max_length = Resume._meta.get_field("title").max_length

        clone = Resume.objects.create(
            owner=request.user,
            title=original.title[:max_length - len(suffix)] + suffix,
            template=original.template,
        )

        personal_info = getattr(original, "personal_info", None)

        if personal_info:
            PersonalInfo.objects.create(
                resume=clone,
                first_name=personal_info.first_name,
                last_name=personal_info.last_name,
                email=personal_info.email,
                phone=personal_info.phone,
                city=personal_info.city,
                about=personal_info.about,
                photo=personal_info.photo.name,
            )

        for education in original.education.all():
            Education.objects.create(
                resume=clone,
                institution=education.institution,
                specialty=education.specialty,
                start_date=education.start_date,
                end_date=education.end_date,
                description=education.description,
            )

        for experience in original.work_experiences.all():
            WorkExperience.objects.create(
                resume=clone,
                company=experience.company,
                position=experience.position,
                start_date=experience.start_date,
                end_date=experience.end_date,
                description=experience.description,
            )

        for skill in original.skills.all():
            Skill.objects.create(
                resume=clone,
                name=skill.name,
                level=skill.level,
            )

        return redirect("resume_detail", pk=clone.pk)