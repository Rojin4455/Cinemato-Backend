# Generated by Django 5.1 on 2024-11-16 07:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking_management', '0004_bookedticket_booking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookedticket',
            name='booking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booking', to='booking_management.booking'),
        ),
    ]