# Generated by Django 4.0.4 on 2022-09-18 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_activity_questions_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='url',
            field=models.CharField(default='', max_length=100),
        ),
    ]
