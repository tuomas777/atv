# Generated by Django 3.2.9 on 2022-09-19 10:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0009_add_type_and_status_display_values"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="deletable",
            field=models.BooleanField(
                default=True,
                help_text="Is document deletable by user.",
                verbose_name="deletable",
            ),
        ),
    ]
