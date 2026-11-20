"""Editors may view newsletter subscribers, not change them (ADR 0014)."""

from django.db import migrations

from core.permissions import grant, revoke

ACTIONS = ("view",)


def forwards(apps, schema_editor):
    grant(apps, "newsletter", "newslettersubscriber", ACTIONS)


def backwards(apps, schema_editor):
    revoke(apps, "newsletter", "newslettersubscriber", ACTIONS)


class Migration(migrations.Migration):
    dependencies = [
        ("newsletter", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("wagtailcore", "0097_baselogentry_uuid_action_timestamp_indexes"),
    ]

    operations = [migrations.RunPython(forwards, backwards)]
