# Generated by Django 4.0.4 on 2022-05-15 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_classroom_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classroom',
            name='name',
            field=models.CharField(default='My Classroom', max_length=20),
        ),
    ]
