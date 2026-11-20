"""Editors may publish pages (ADR 0014: the editor publishes her own work).

Wagtail's initial data gives the "Editors" group only add and edit on the
page tree; this adds publish on the root page, which covers all pages.
"""

from django.db import migrations

from core.permissions import EDITORS, permissions


def forwards(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Page = apps.get_model("wagtailcore", "Page")
    GroupPagePermission = apps.get_model("wagtailcore", "GroupPagePermission")
    group, _ = Group.objects.get_or_create(name=EDITORS)
    root = Page.objects.get(depth=1)
    [publish] = permissions(apps, "wagtailcore", "page", ["publish"])
    GroupPagePermission.objects.get_or_create(
        group=group, page=root, permission=publish
    )


def backwards(apps, schema_editor):
    GroupPagePermission = apps.get_model("wagtailcore", "GroupPagePermission")
    GroupPagePermission.objects.filter(
        group__name=EDITORS, page__depth=1, permission__codename="publish_page"
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("stories", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("wagtailcore", "0097_baselogentry_uuid_action_timestamp_indexes"),
    ]

    operations = [migrations.RunPython(forwards, backwards)]
