# Generated by Django 5.1 on 2024-11-24 10:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_management', '0006_alter_movie_description_alter_movie_vote_average'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(max_length=100, unique=True)),
                ('rated_at', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('rating', models.PositiveSmallIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('likes_count', models.PositiveIntegerField(default=0)),
                ('dislikes_count', models.PositiveIntegerField(default=0)),
                ('hashtags', models.ManyToManyField(related_name='reviews', to='movie_management.hashtag')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='movie_management.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReviewReaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reaction', models.CharField(choices=[('like', 'Like'), ('dislike', 'Dislike')], max_length=7)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reactions', to='movie_management.review')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_reactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'review')},
            },
        ),
    ]