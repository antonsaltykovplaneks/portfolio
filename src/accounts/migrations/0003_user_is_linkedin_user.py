# Generated by Django 4.2.9 on 2024-08-23 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_is_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_linkedin_user',
            field=models.BooleanField(default=False, help_text='Designates whether the user is a LinkedIn user.', verbose_name='LinkedIn user'),
        ),
    ]
