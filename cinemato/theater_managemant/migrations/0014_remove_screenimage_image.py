# Generated by Django 5.1 on 2024-10-15 09:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('theater_managemant', '0013_remove_theater_image_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='screenimage',
            name='image',
        ),
    ]
