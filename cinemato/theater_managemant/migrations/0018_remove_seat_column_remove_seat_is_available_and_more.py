# Generated by Django 5.1 on 2024-10-18 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theater_managemant', '0017_delete_sampleimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seat',
            name='column',
        ),
        migrations.RemoveField(
            model_name='seat',
            name='is_available',
        ),
        migrations.RemoveField(
            model_name='seat',
            name='row',
        ),
        migrations.AddField(
            model_name='seat',
            name='seat_layout',
            field=models.JSONField(default=' '),
        ),
    ]