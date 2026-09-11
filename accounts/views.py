from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from .forms import ProfileForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class CreateUserView(CreateView):
    form_class = UserCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("login")

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class =  ProfileForm
    template_name =  "accounts/profile.html"
    success_url = reverse_lazy("resume_list")

    def get_object(self):
        return self.request.user