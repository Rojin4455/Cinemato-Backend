# Generated by Django 5.1 on 2024-11-24 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_management', '0009_alter_review_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.DecimalField(decimal_places=2, max_digits=3),
        ),
    ]