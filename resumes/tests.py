from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Education, PersonalInfo, Resume, WorkExperience


class ResumeSectionEditingTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="owner")
        self.other = get_user_model().objects.create_user(username="other")
        self.resume = Resume.objects.create(owner=self.owner, title="My CV")
        self.sections = [
            ("personal_info", PersonalInfo.objects.create(
                resume=self.resume, first_name="Old", last_name="Name",
                email="old@example.com",
            ), {"first_name": "New", "last_name": "Name", "email": "new@example.com"}, "first_name"),
            ("education", Education.objects.create(
                resume=self.resume, institution="Old", start_date="2020-09-01",
            ), {"institution": "New", "start_date": "2020-09-01"}, "institution"),
            ("work_experience", WorkExperience.objects.create(
                resume=self.resume, company="Old", description="Work", start_date="2022-01-01",
            ), {"company": "New", "description": "Updated", "start_date": "2022-01-01"}, "company"),
        ]

    def test_owner_can_edit_and_delete_sections(self):
        self.client.force_login(self.owner)
        detail_url = reverse("resume_detail", args=[self.resume.pk])
        for name, obj, data, field in self.sections:
            with self.subTest(section=name):
                edit_url = reverse(f"{name}_update", args=[obj.pk])
                delete_url = reverse(f"{name}_delete", args=[obj.pk])
                detail = self.client.get(detail_url)
                self.assertContains(detail, edit_url)
                self.assertContains(detail, delete_url)
                edit = self.client.get(edit_url)
                self.assertEqual(edit.status_code, 200)
                if "start_date" in data:
                    self.assertContains(edit, f'value="{data["start_date"]}"')
                response = self.client.post(edit_url, data)
                self.assertRedirects(response, detail_url)
                obj.refresh_from_db()
                self.assertEqual(getattr(obj, field), "New")
                self.assertEqual(self.client.get(delete_url).status_code, 200)
                self.assertTrue(type(obj).objects.filter(pk=obj.pk).exists())
                self.assertRedirects(self.client.post(delete_url), detail_url)
                self.assertFalse(type(obj).objects.filter(pk=obj.pk).exists())
                self.assertTrue(Resume.objects.filter(pk=self.resume.pk).exists())
        self.assertContains(self.client.get(detail_url), reverse("personal_info_create", args=[self.resume.pk]))

    def test_other_user_cannot_access_or_change_sections(self):
        self.client.force_login(self.other)
        for name, obj, data, field in self.sections:
            for action in ("update", "delete"):
                with self.subTest(section=name, action=action):
                    url = reverse(f"{name}_{action}", args=[obj.pk])
                    self.assertEqual(self.client.get(url).status_code, 404)
                    self.assertEqual(self.client.post(url, data).status_code, 404)
                    obj.refresh_from_db()
                    self.assertEqual(getattr(obj, field), "Old")

    def test_anonymous_requests_require_login(self):
        for name, obj, data, _ in self.sections:
            for action in ("update", "delete"):
                url = reverse(f"{name}_{action}", args=[obj.pk])
                for response in (self.client.get(url), self.client.post(url, data)):
                    self.assertEqual(response.status_code, 302)
                    self.assertIn("/accounts/login/", response.url)
                self.assertTrue(type(obj).objects.filter(pk=obj.pk).exists())

    def test_invalid_personal_info_does_not_overwrite_saved_data(self):
        self.client.force_login(self.owner)
        obj = self.sections[0][1]
        response = self.client.post(reverse("personal_info_update", args=[obj.pk]), {
            "first_name": "", "last_name": "Name", "email": "invalid",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        obj.refresh_from_db()
        self.assertEqual(obj.first_name, "Old")
