# Generated by Django 4.2.9 on 2024-09-12 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0010_projectsetlinkaccess_view_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailstatus',
            name='status',
            field=models.CharField(choices=[('sent', 'sent'), ('delivered', 'delivered'), ('failed', 'failed'), ('opened', 'opened'), ('ignored', 'ignored')], default='sent', max_length=20),
        ),
    ]
