import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction

from .models import Resume, ResumeVersion, PersonalInfo, Education, WorkExperience, Skill


SECTION_FIELDS = {
    "personal_info": (PersonalInfo, ("first_name", "last_name", "email", "phone", "city", "about", "photo")),
    "education": (Education, ("institution", "specialty", "start_date", "end_date", "description")),
    "work_experiences": (WorkExperience, ("company", "position", "start_date", "end_date", "description")),
    "skills": (Skill, ("name", "level")),
}


def snapshot_resume(resume):
    snapshot = {"schema": 1, "title": resume.title, "template": resume.template}
    for name, (model, fields) in SECTION_FIELDS.items():
        rows = list(model.objects.filter(resume=resume).order_by("pk").values(*fields))
        snapshot[name] = (rows[0] if rows else None) if name == "personal_info" else rows
    return json.loads(json.dumps(snapshot, cls=DjangoJSONEncoder))


def save_version(resume, label=""):
    return ResumeVersion.objects.create(
        resume=resume, label=label, snapshot=snapshot_resume(resume)
    )


@transaction.atomic
def restore_version(version):
    resume = Resume.objects.select_for_update().get(pk=version.resume_id)
    snapshot = version.snapshot
    if snapshot.get("schema") != 1:
        raise ValueError("Unsupported resume version schema")
    save_version(resume, "Перед відновленням версії")
    resume.title = snapshot["title"]
    resume.template = snapshot["template"]
    resume.save(update_fields=["title", "template", "updated_at"])
    for name, (model, fields) in SECTION_FIELDS.items():
        model.objects.filter(resume=resume).delete()
        rows = snapshot[name]
        if name == "personal_info":
            rows = [rows] if rows else []
        for row in rows:
            model.objects.create(resume=resume, **{field: row[field] for field in fields})
    return resume
