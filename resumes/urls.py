from django.urls import path
from . import views
from .views import ResumeCreateView, ResumePDFView, ResumeDetailView, ResumeUpdateView, ResumeDeleteView, PersonalInfoCreateView, EducationCreateView, WorkExperienceCreateView, SkillCreateView, SkillUpdateView, SkillDeleteView

urlpatterns = [
    path("", views.resume_list, name="resume_list"),
    path("create/", ResumeCreateView.as_view(), name="resume_create"),
    path("resume/<int:pk>/pdf/", ResumePDFView.as_view(), name="resume_pdf"),
    path("resume/<int:pk>/", ResumeDetailView.as_view(), name="resume_detail"),
    path("resume/edit/<int:pk>/", ResumeUpdateView.as_view(), name="resume_update"),
    path("resume/delete/<int:pk>/",ResumeDeleteView.as_view(),name="resume_delete"),
    path("resume/<int:pk>/personal-info/", PersonalInfoCreateView.as_view(), name="personal_info_create"),
    path("resume/<int:pk>/education/", EducationCreateView.as_view(), name="education_create"),
    path("resume/<int:pk>/work-experience/", WorkExperienceCreateView.as_view(), name="work_experience_create"),
    path("resume/<int:pk>/skills/",SkillCreateView.as_view(),name="skill_create"),
    path("skill/edit/<int:pk>/",SkillUpdateView.as_view(),name="skill_update"),
    path("skill/delete/<int:pk>/",SkillDeleteView.as_view(),name="skill_delete"),
    path("personal-info/edit/<int:pk>/", views.PersonalInfoUpdateView.as_view(), name="personal_info_update"),
    path("personal-info/delete/<int:pk>/", views.PersonalInfoDeleteView.as_view(), name="personal_info_delete"),
    path("education/edit/<int:pk>/", views.EducationUpdateView.as_view(), name="education_update"),
    path("education/delete/<int:pk>/", views.EducationDeleteView.as_view(), name="education_delete"),
    path("work-experience/edit/<int:pk>/", views.WorkExperienceUpdateView.as_view(), name="work_experience_update"),
    path("work-experience/delete/<int:pk>/", views.WorkExperienceDeleteView.as_view(), name="work_experience_delete"),
]
