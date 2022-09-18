from django.db import models
import datetime
import random
# from django.dispatch import receiver
# from django.urls import reverse
# from django_rest_passwordreset.signals import reset_password_token_created
# from django.core.mail import send_mail  


# @receiver(reset_password_token_created)
# def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

#     email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)

#     send_mail(
#         # title:
#         "Password Reset for {title}".format(title="Todos"),
#         # message:
#         email_plaintext_message,
#         # from:
#         "zach@talktodos.com",
#         # to:
#         [reset_password_token.user.email]
#     )

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
    name = models.CharField(max_length=100, default="")
    questions = models.CharField(max_length=1500, default="")
    url = models.CharField(max_length=100, default="")
    num = models.IntegerField(default=0)

class Activity(models.Model):
    name = models.CharField(max_length=100, default="")
    description = models.CharField(max_length=1500, default="")
    num = models.IntegerField(default=0)
