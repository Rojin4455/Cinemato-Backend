# Generated by Django 5.1 on 2024-10-19 12:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('theater_managemant', '0020_remove_theater_photo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='theater',
            name='total_screens',
        ),
    ]
