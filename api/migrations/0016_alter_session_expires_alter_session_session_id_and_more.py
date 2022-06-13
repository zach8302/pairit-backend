# Generated by Django 4.0.4 on 2022-06-12 16:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_session_token_alter_session_expires_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 12, 16, 46, 48, 35062)),
        ),
        migrations.AlterField(
            model_name='session',
            name='session_id',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='session',
            name='token',
            field=models.CharField(default='', max_length=500),
        ),
    ]