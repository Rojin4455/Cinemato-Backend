# Generated by Django 5.1 on 2024-12-17 07:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_userlocation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userlocation',
            name='geom',
        ),
    ]