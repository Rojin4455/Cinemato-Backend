# Generated by Django 5.1 on 2024-10-18 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theater_managemant', '0018_remove_seat_column_remove_seat_is_available_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seat',
            name='seat_layout',
            field=models.JSONField(),
        ),
    ]