# Generated by Django 5.1 on 2024-10-25 07:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_management', '0004_alter_person_image'),
        ('screen_management', '0005_alter_showtime_unique_together'),
        ('theater_managemant', '0023_alter_seat_column_alter_seat_identifier_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MovieSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='movie_management.movie')),
                ('showtime', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='screen_management.showtime')),
            ],
        ),
        migrations.CreateModel(
            name='DailyShow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('show_date', models.DateField()),
                ('show_time', models.TimeField()),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_shows', to='screen_management.movieschedule')),
            ],
            options={
                'unique_together': {('schedule', 'show_date', 'show_time')},
            },
        ),
        migrations.CreateModel(
            name='SeatBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('booked', 'Booked'), ('reserved', 'Reserved'), ('available', 'Available')], default='available', max_length=10)),
                ('seat_row', models.CharField(max_length=5)),
                ('seat_column', models.PositiveIntegerField()),
                ('tier_row', models.IntegerField()),
                ('tier_column', models.IntegerField()),
                ('identifier', models.CharField(blank=True, max_length=5, null=True)),
                ('tier_name', models.CharField(max_length=50)),
                ('tier_price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('daily_show', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seat_bookings', to='screen_management.dailyshow')),
                ('seat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='theater_managemant.seat')),
            ],
            options={
                'unique_together': {('daily_show', 'seat')},
            },
        ),
    ]
