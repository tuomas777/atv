# Generated by Django 3.2.6 on 2021-09-14 07:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("audit_log", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="auditlogentry",
            options={"verbose_name_plural": "audit log entries"},
        ),
    ]
