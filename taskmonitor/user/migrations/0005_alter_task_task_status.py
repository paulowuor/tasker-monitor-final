# Generated by Django 5.0 on 2024-01-05 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_alter_notification_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='task_status',
            field=models.CharField(choices=[('active', 'active'), ('completed', 'completed'), ('cancelled', 'cancelled'), ('expired', 'expired')], default='active', max_length=20),
        ),
    ]
