# Generated by Django 5.0.2 on 2024-02-28 05:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_user_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='logo',
            field=models.CharField(default=datetime.datetime(2024, 2, 28, 5, 50, 10, 237387, tzinfo=datetime.timezone.utc), max_length=1000, verbose_name='Logo'),
            preserve_default=False,
        ),
    ]
