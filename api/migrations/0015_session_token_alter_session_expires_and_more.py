# Generated by Django 4.0.4 on 2022-06-11 20:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_session_expires'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='token',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='session',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 11, 20, 55, 40, 365290)),
        ),
        migrations.AlterField(
            model_name='session',
            name='session_id',
            field=models.CharField(default='', max_length=50),
        ),
    ]
