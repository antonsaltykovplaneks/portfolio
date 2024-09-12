# Generated by Django 4.2.9 on 2024-09-12 06:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("infrastructure", "0008_alter_projectsetlink_project_set_emailstatus"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="projectsetlinkaccess",
            name="ip_address",
        ),
        migrations.AddField(
            model_name="projectsetlinkaccess",
            name="ip_address_hash",
            field=models.CharField(max_length=255),
            preserve_default=False,
        ),
    ]
