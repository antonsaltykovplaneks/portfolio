# Generated by Django 4.2.9 on 2024-09-05 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0002_project_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title of the project set', max_length=255)),
                ('is_public', models.BooleanField(default=False, help_text='If the project set is public or not')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('projects', models.ManyToManyField(related_name='project_sets', to='infrastructure.project')),
            ],
            options={
                'verbose_name': 'Project set',
                'verbose_name_plural': 'Project sets',
            },
        ),
    ]
