# Generated by Django 5.0.1 on 2024-01-08 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_screenshot_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='finish_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
