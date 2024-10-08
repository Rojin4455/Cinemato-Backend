# Generated by Django 5.1 on 2024-09-18 11:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tmdb_id', models.IntegerField()),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('image', models.ImageField(blank=True, null=True, upload_to='movies/persons/')),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('tmdb_id', models.IntegerField()),
                ('release_date', models.DateField()),
                ('vote_average', models.FloatField()),
                ('runtime', models.IntegerField()),
                ('description', models.TextField()),
                ('poster_path', models.URLField(blank=True, max_length=500, null=True)),
                ('backdrop_path', models.URLField(blank=True, max_length=500, null=True)),
                ('video_key', models.CharField(max_length=225)),
                ('is_listed', models.BooleanField(default=True)),
                ('genres', models.ManyToManyField(related_name='movies', to='movie_management.genre')),
                ('languages', models.ManyToManyField(related_name='movies', to='movie_management.language')),
            ],
        ),
        migrations.CreateModel(
            name='MovieRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(blank=True, max_length=50, null=True)),
                ('character_name', models.CharField(blank=True, max_length=255, null=True)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='movie_management.movie')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='movie_management.person')),
            ],
        ),
    ]
