# Generated by Django 4.0.4 on 2022-06-23 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_classroom_is_subscribed'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='email',
            field=models.CharField(default='', max_length=100, unique=True),
        ),
    ]
