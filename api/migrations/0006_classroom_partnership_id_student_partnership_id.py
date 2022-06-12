# Generated by Django 4.0.4 on 2022-05-15 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_student_personality'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='partnership_id',
            field=models.CharField(max_length=10, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='student',
            name='partnership_id',
            field=models.CharField(max_length=10, null=True, unique=True),
        ),
    ]
