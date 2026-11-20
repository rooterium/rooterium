"""Replace Wagtail's default welcome page with the Rooterium home page."""

import uuid

from django.db import migrations


def create_homepage(apps, schema_editor):
    ContentType = apps.get_model("contenttypes.ContentType")
    Locale = apps.get_model("wagtailcore.Locale")
    Page = apps.get_model("wagtailcore.Page")
    Site = apps.get_model("wagtailcore.Site")
    HomePage = apps.get_model("home.HomePage")

    # The welcome page from wagtailcore's initial data (its Site cascades).
    page_type = ContentType.objects.get(app_label="wagtailcore", model="page")
    Page.objects.filter(content_type=page_type, slug="home", depth=2).delete()

    homepage_type, _ = ContentType.objects.get_or_create(
        app_label="home", model="homepage"
    )
    homepage = HomePage.objects.create(
        title="Rooterium",
        draft_title="Rooterium",
        slug="home",
        content_type=homepage_type,
        path="00010001",
        depth=2,
        numchild=0,
        url_path="/home/",
        locale=Locale.objects.order_by("pk").first(),
        translation_key=uuid.uuid4(),
        live=True,
    )
    Site.objects.create(
        hostname="localhost",
        site_name="Rooterium",
        root_page=homepage,
        is_default_site=True,
    )


def remove_homepage(apps, schema_editor):
    ContentType = apps.get_model("contenttypes.ContentType")
    HomePage = apps.get_model("home.HomePage")
    HomePage.objects.filter(slug="home", depth=2).delete()
    ContentType.objects.filter(app_label="home", model="homepage").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0001_initial"),
        ("wagtailcore", "0097_baselogentry_uuid_action_timestamp_indexes"),
    ]

    operations = [migrations.RunPython(create_homepage, remove_homepage)]
