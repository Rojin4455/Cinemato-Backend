# Generated by Django 5.1 on 2024-10-18 12:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('theater_managemant', '0019_alter_seat_seat_layout'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='theater',
            name='photo',
        ),
    ]