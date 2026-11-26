"""Move places from the version 1 themes to the six sections (ADR 0018):
Myths → Religion, Traditions → History.

Updates the live row and every stored revision, so the admin's edit form
(which loads the latest revision) never shows a value that is no longer a
choice. Section pages are restructured by the `restructure_sections`
command instead: moving pages needs Wagtail's tree API, which historical
models in migrations do not have.
"""

from django.db import migrations

MAPPING = {"myths": "religion", "traditions": "history"}


def remap(apps, mapping):
    Place = apps.get_model("places", "Place")
    Revision = apps.get_model("wagtailcore", "Revision")
    ContentType = apps.get_model("contenttypes", "ContentType")
    for old, new in mapping.items():
        Place.objects.filter(theme=old).update(theme=new)
    content_type = ContentType.objects.filter(app_label="places", model="place").first()
    if not content_type:
        return
    for revision in Revision.objects.filter(content_type=content_type):
        theme = revision.content.get("theme")
        if theme in mapping:
            revision.content["theme"] = mapping[theme]
            revision.save(update_fields=["content"])


def forwards(apps, schema_editor):
    remap(apps, MAPPING)


class Migration(migrations.Migration):
    dependencies = [
        ("places", "0003_place_section_choices"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("wagtailcore", "0097_baselogentry_uuid_action_timestamp_indexes"),
    ]

    # Not reversible in a meaningful way (History and Religion also hold
    # places that were never Traditions or Myths): reversing is a no-op.
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
