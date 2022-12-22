# Generated by Django 3.2.16 on 2022-12-15 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0006_serviceapikey_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="serviceapikey",
            name="hashed_key",
            field=models.CharField(editable=False, max_length=150),
        ),
        migrations.AlterField(
            model_name="serviceapikey",
            name="id",
            field=models.CharField(
                editable=False,
                max_length=150,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
    ]
