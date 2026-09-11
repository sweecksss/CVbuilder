from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.urls import reverse

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

        html_string = render_to_string(
            "resumes/resume_pdf.html",
            {"resume": self.object}
        )

        pdf = HTML(
            string=html_string,
            base_url=request.build_absolute_uri("/")
        ).write_pdf()

        response = HttpResponse(
            pdf,
            content_type="application/pdf"
        )

        response["Content-Disposition"] = (
            f'attachment; filename="{self.object.title}.pdf"'
        )

        return response

class ResumeDetailView(LoginRequiredMixin, DetailView):
    model = Resume
    template_name = "resumes/resume_detail.html"

    def get_queryset(self):
        return Resume.objects.filter(owner=self.request.user)

class ResumeUpdateView(LoginRequiredMixin, UpdateView):
    model = Resume
    fields = ["title"]
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
