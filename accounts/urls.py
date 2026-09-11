from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import CreateUserView, ProfileUpdateView

urlpatterns = [
    path("login/",LoginView.as_view(template_name="accounts/login.html"),name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", CreateUserView.as_view(), name="register"),
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
    
]