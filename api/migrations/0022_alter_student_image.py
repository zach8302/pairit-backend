# Generated by Django 4.0.4 on 2022-06-12 18:34

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_alter_student_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='image',
            field=models.IntegerField(default=0),
        ),
    ]
