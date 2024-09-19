# accounts/migrations/0006_update_django_admin_log.py

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0002_auto_20230918_1234'),  # Replace with latest admin migration
        ('accounts','0004_userprofile'),  # Replace with the latest accounts migration
    ]

    operations = [
        migrations.AlterField(
            model_name='logentry',  # This is the model for django_admin_log
            name='user',
            field=models.ForeignKey(
                to='accounts.User',  # Reference to your custom user model
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True,
            ),
        ),
    ]
