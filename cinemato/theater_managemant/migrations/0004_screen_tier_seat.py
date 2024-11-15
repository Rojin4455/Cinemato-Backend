# Generated by Django 5.1 on 2024-10-08 13:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theater_managemant', '0003_theater_is_approved'),
    ]

    operations = [
        migrations.CreateModel(
            name='Screen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=50)),
                ('capacity', models.PositiveIntegerField(null=True)),
                ('theater', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='screens', to='theater_managemant.theater')),
            ],
        ),
        migrations.CreateModel(
            name='Tier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, default=1.0, max_digits=5)),
                ('total_seats', models.PositiveIntegerField()),
                ('screen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tiers', to='theater_managemant.screen')),
            ],
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row', models.CharField(max_length=5)),
                ('column', models.PositiveIntegerField()),
                ('is_available', models.BooleanField(default=False)),
                ('tier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seats', to='theater_managemant.tier')),
            ],
        ),
    ]
