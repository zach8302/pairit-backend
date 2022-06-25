from django.db import models
import datetime
import random

# Create your models here.
class Classroom(models.Model):
    first = models.CharField(max_length=100, null=False)
    owner = models.CharField(max_length=100, null=False)
    class_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, default="My Classroom", unique=False)
    email = models.CharField(max_length=100, default="", unique=True, null=False)
    partnership_id = models.CharField(max_length=10, unique=False, null=True)
    is_ready = models.BooleanField(default=False)
    num_calls = models.IntegerField(default=0)
    expires = models.DateTimeField(default=None, null=True)

class Student(models.Model):
    first = models.CharField(max_length=100, null=False)
    username = models.CharField(max_length=100, unique=True)
    class_id = models.CharField(max_length=10, unique=False)
    personality = models.IntegerField(unique=False, default=0)
    partnership_id = models.CharField(max_length=10, unique=False, null=True)
    image = models.IntegerField(default=0)

class Session(models.Model):
    partnership_id = models.CharField(max_length=10, unique=True, null=True)
    class_id = models.CharField(max_length=10, unique=False, null=True)
    session_id = models.CharField(max_length=500, default="")
    token = models.CharField(max_length=500, default="")
    active = models.BooleanField(default=False)
    expires = models.DateTimeField(default=None)

class Questions(models.Model):
    questions = models.CharField(max_length=1500, default="")
    num = models.IntegerField(default=0)
