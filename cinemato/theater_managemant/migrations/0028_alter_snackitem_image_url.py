# Generated by Django 5.1 on 2024-11-08 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theater_managemant', '0027_alter_snackitem_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snackitem',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]