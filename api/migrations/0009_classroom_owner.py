# Generated by Django 4.0.4 on 2022-06-05 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_session_classroom_is_ready'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='owner',
            field=models.CharField(default=None, max_length=20),
            preserve_default=False,
        ),
    ]
