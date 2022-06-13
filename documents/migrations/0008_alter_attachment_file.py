# Generated by Django 3.2.9 on 2022-06-08 14:15

from django.db import migrations
import documents.fields
import documents.utils


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0007_alter_document_content"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attachment",
            name="file",
            field=documents.fields.EncryptedFileField(
                help_text="Encrypted file.",
                upload_to=documents.utils.get_attachment_file_path,
                verbose_name="file",
            ),
        ),
    ]
