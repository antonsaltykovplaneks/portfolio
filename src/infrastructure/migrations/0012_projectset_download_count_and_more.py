# Generated by Django 4.2.9 on 2024-09-16 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0011_alter_emailstatus_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectset',
            name='download_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='projectset',
            name='shared_link_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
