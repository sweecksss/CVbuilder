from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Resume(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='resumes'
    )

    title = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class PersonalInfo(models.Model):
    resume = models.OneToOneField(
        Resume,
        on_delete=models.CASCADE,
        related_name="personal_info"
    )

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=100, blank=True)
    about = models.TextField(blank=True)
    photo = models.ImageField(
        upload_to="resume_photos/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Education(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='education'
    )

    institution = models.CharField(max_length=64, blank=True)
    specialty = models.CharField(max_length=64, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)

class WorkExperience(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='work_experiences'
    )

    company = models.CharField(max_length=64, blank=True)
    position = models.CharField(max_length=128, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField()