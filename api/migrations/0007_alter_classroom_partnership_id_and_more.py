# Generated by Django 4.0.4 on 2022-05-16 00:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_classroom_partnership_id_student_partnership_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classroom',
            name='partnership_id',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='partnership_id',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='personality',
            field=models.IntegerField(default=0),
        ),
    ]
