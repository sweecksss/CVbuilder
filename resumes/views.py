from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST, require_http_methods
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
from io import BytesIO
from docx import Document
from docx.shared import Cm
from PIL import Image, ImageOps

from .models import Resume, PersonalInfo, Education, WorkExperience, Skill, ResumeVersion
from .forms import ResumeForm, PersonalInfoForm, EducationForm, WorkExperienceForm, SkillForm, ResumeVersionForm
from .versioning import save_version, restore_version

# Create your views here.

RESUME_TEMPLATES = [
    {"key": "sidebar", "name": "З бічною колонкою", "description": "Контрастний дизайн: контакти та навички збоку, досвід у центрі уваги."},
    {"key": "classic", "name": "Класичний", "description": "Чиста структура, стримані акценти та максимум уваги до вашого досвіду."},
    {"key": "modern", "name": "Сучасний", "description": "М’які зелені акценти, компактна шапка та виразні блоки навичок."},
]


def home(request):
    return render(request, "resumes/home.html", {"templates": RESUME_TEMPLATES})


def template_catalog(request):
    return render(request, "resumes/template_catalog.html", {"templates": RESUME_TEMPLATES})


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

    def get_initial(self):
        initial = super().get_initial()
        selected = self.request.GET.get("template")
        if selected in dict(Resume._meta.get_field("template").choices):
            initial["template"] = selected
        return initial

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

class ResumeDOCXView(LoginRequiredMixin, DetailView):
    model = Resume

    def get_queryset(self):
        return Resume.objects.filter(owner=self.request.user)

    def get(self, request, *args, **kwargs):
        resume = self.get_object()
        document = Document()

        document.add_heading(resume.title, level=0)

        personal_info = getattr(resume, "personal_info", None)

        if personal_info:
            if personal_info.photo:
                with personal_info.photo.open("rb") as photo:
                    with Image.open(photo) as image:
                        photo_buffer = BytesIO()
                        ImageOps.exif_transpose(image).convert("RGB").save(
                            photo_buffer, format="PNG"
                        )
                photo_buffer.seek(0)
                document.add_picture(photo_buffer, width=Cm(3))

            document.add_heading(
                f"{personal_info.first_name} {personal_info.last_name}",
                level=1,
            )

            for contact in [
                personal_info.email,
                personal_info.phone,
                personal_info.city,
            ]:
                if contact:
                    document.add_paragraph(contact)

            if personal_info.about:
                document.add_heading("Про себе", level=1)
                document.add_paragraph(personal_info.about)

        experiences = resume.work_experiences.all()

        if experiences:
            document.add_heading("Досвід роботи", level=1)

            for experience in experiences:
                document.add_heading(
                    experience.position or experience.company,
                    level=2,
                )
                if experience.position and experience.company:
                    document.add_paragraph(experience.company)
                if experience.start_date:
                    document.add_paragraph(f"Початок: {experience.start_date:%m.%Y}")
                if experience.end_date:
                    document.add_paragraph(f"Кінець: {experience.end_date:%m.%Y}")
                if experience.description:
                    document.add_paragraph(experience.description)

        education_list = resume.education.all()

        if education_list:
            document.add_heading("Освіта", level=1)

            for education in education_list:
                document.add_heading(education.institution, level=2)
                if education.specialty:
                    document.add_paragraph(education.specialty)
                if education.start_date:
                    document.add_paragraph(f"Початок: {education.start_date:%m.%Y}")
                if education.end_date:
                    document.add_paragraph(f"Кінець: {education.end_date:%m.%Y}")
                if education.description:
                    document.add_paragraph(education.description)

        skills = resume.skills.all()

        if skills:
            document.add_heading("Навички", level=1)

            for skill in skills:
                text = skill.name
                if skill.level:
                    text += f" — {skill.level}"
                document.add_paragraph(text, style="List Bullet")

        buffer = BytesIO()
        document.save(buffer)

        response = HttpResponse(
            buffer.getvalue(),
            content_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
        )
        response["Content-Disposition"] = 'attachment; filename="resume.docx"'

        return response

@login_required
def resume_versions(request, pk):

    resume = get_object_or_404(Resume, pk=pk, owner=request.user)
    page = Paginator(resume.versions.all(), 10).get_page(request.GET.get("page"))
    return render(request, "resumes/resume_versions.html", {
        "resume": resume, "page_obj": page, "form": ResumeVersionForm(),
    })


@login_required
@require_POST
@transaction.atomic
def resume_version_create(request, pk):

    resume = get_object_or_404(
        Resume.objects.select_for_update(), pk=pk, owner=request.user
    )
    form = ResumeVersionForm(request.POST)
    if not form.is_valid():
        return render(request, "resumes/resume_versions.html", {
            "resume": resume, "form": form,
            "page_obj": Paginator(resume.versions.all(), 10).get_page(1),
        }, status=400)
    save_version(resume, form.cleaned_data["label"])
    messages.success(request, "Версію збережено.")
    return redirect("resume_versions", pk=resume.pk)


@login_required
@require_http_methods(["GET", "POST"])
def resume_version_restore(request, pk, version_pk):

    version = get_object_or_404(
        ResumeVersion.objects.select_related("resume"), pk=version_pk,
        resume_id=pk, resume__owner=request.user,
    )
    if request.method == "POST":
        restore_version(version)
        messages.success(request, "Версію відновлено. Попередній стан також збережено в історії.")
        return redirect("resume_versions", pk=pk)
    return render(request, "resumes/resume_version_restore.html", {
        "version": version, "resume": version.resume,
    })
