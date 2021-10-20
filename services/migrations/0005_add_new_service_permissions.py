# Generated by Django 3.2.7 on 2021-10-19 11:05

from django.db import migrations


def remove_manage_permissions(apps, schema_editor):
    """Remove old permissions."""
    ContentType = apps.get_model("contenttypes.ContentType")
    Permission = apps.get_model("auth.Permission")
    content_type = ContentType.objects.filter(
        model="service",
        app_label="services",
    ).first()
    if content_type:
        # New content types are created with a post-migrate hook. This means
        # that for a fresh DB the content types might not exist yet.
        Permission.objects.filter(
            content_type=content_type,
            codename__in=("can_manage_documents", "can_manage_attachments"),
        ).delete()


def remove_fine_grained_permissions(apps, schema_editor):
    """Reverse new permissions."""
    ContentType = apps.get_model("contenttypes.ContentType")
    Permission = apps.get_model("auth.Permission")
    content_type = ContentType.objects.get(
        model="service",
        app_label="services",
    )
    Permission.objects.filter(
        content_type=content_type,
        codename__in=(
            "can_add_documents",
            "can_change_documents",
            "can_delete_documents",
            "can_add_attachments",
            "can_change_attachments",
            "can_delete_attachments",
        ),
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0004_add_serviceclientid"),
    ]

    operations = [
        migrations.RunPython(remove_manage_permissions, migrations.RunPython.noop),
        migrations.RunPython(
            migrations.RunPython.noop, remove_fine_grained_permissions
        ),
        migrations.AlterModelOptions(
            name="service",
            options={
                "permissions": [
                    ("can_add_documents", "Can add documents"),
                    ("can_change_documents", "Can change documents"),
                    ("can_delete_documents", "Can delete documents"),
                    ("can_view_documents", "Can view documents"),
                    ("can_add_attachments", "Can add attachments"),
                    ("can_change_attachments", "Can change attachments"),
                    ("can_delete_attachments", "Can delete attachments"),
                    ("can_view_attachments", "Can view attachments"),
                ],
                "verbose_name": "service",
                "verbose_name_plural": "services",
            },
        ),
    ]
