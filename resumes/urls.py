from django.urls import path
from . import views
from .views import ResumeCreateView, ResumePDFView, ResumeDetailView, ResumeUpdateView, ResumeDeleteView, PersonalInfoCreateView, EducationCreateView, WorkExperienceCreateView

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
]