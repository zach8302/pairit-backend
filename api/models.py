from django.db import models
import datetime

# Create your models here.
class Classroom(models.Model):
    first = models.CharField(max_length=100, null=False)
    owner = models.CharField(max_length=100, null=False)
    class_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, default="My Classroom", unique=False)
    partnership_id = models.CharField(max_length=10, unique=False, null=True)
    is_ready = models.BooleanField(default=False)

class Student(models.Model):
    first = models.CharField(max_length=100, null=False)
    username = models.CharField(max_length=100, unique=True)
    class_id = models.CharField(max_length=10, unique=False)
    personality = models.IntegerField(unique=False, default=0)
    partnership_id = models.CharField(max_length=10, unique=False, null=True)

class Session(models.Model):
    partnership_id = models.CharField(max_length=10, unique=True, null=True)
    class_id = models.CharField(max_length=10, unique=False, null=True)
    session_id = models.CharField(max_length=500, default="")
    token = models.CharField(max_length=500, default="")
    active = models.BooleanField(default=False)
    expires = models.DateTimeField(default=datetime.datetime.now() + datetime.timedelta(minutes=20))
