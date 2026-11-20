"""Helpers for data migrations that give the editor group its permissions.

Editors are members of Wagtail's "Editors" group, never superusers (ADR
0014). Each content app grants its own permissions in a data migration.
Permissions are created here if missing: Django and Wagtail only create
them after all migrations have run (post_migrate), which is too late on a
fresh database.
"""

EDITORS = "Editors"


def permissions(apps, app_label, model_name, actions):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")
    model = apps.get_model(app_label, model_name)
    content_type, _ = ContentType.objects.get_or_create(
        app_label=app_label, model=model._meta.model_name
    )
    return [
        Permission.objects.get_or_create(
            content_type=content_type,
            codename=f"{action}_{model._meta.model_name}",
            defaults={"name": f"Can {action} {model._meta.verbose_name_raw}"},
        )[0]
        for action in actions
    ]


def grant(apps, app_label, model_name, actions, group_name=EDITORS):
    Group = apps.get_model("auth", "Group")
    group, _ = Group.objects.get_or_create(name=group_name)
    group.permissions.add(*permissions(apps, app_label, model_name, actions))


def revoke(apps, app_label, model_name, actions, group_name=EDITORS):
    Group = apps.get_model("auth", "Group")
    group = Group.objects.filter(name=group_name).first()
    if group:
        group.permissions.remove(*permissions(apps, app_label, model_name, actions))
