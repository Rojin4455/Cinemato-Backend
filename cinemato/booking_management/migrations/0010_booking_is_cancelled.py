# Generated by Django 5.1 on 2024-11-22 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking_management', '0009_alter_bookedticket_booking_alter_ordersnack_booking'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='is_cancelled',
            field=models.BooleanField(default=False),
        ),
    ]
