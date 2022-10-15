from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import ensure_csrf_cookie

from .class_views import get_current_classroom
from .student_views import get_current_student
from ..serializers import ClassroomSerializer, StudentSerializer
from ..models import Classroom, Student

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny


class UserExistsView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        student, teacher, teacher_email = None, None, None
        if 'username' in request.data:
            username = request.data.get('username')
            student_response = Student.objects.filter(username=username)
            if student_response:
                student = student_response[0].username
            teacher_response = Classroom.objects.filter(owner=username)
            if teacher_response:
                teacher = teacher_response[0].owner
        if 'email' in request.data:
            email = request.data.get('email')
            teacher_email_response = Classroom.objects.filter(email=email)
            if teacher_email_response:
                teacher_email = teacher_email_response[0].email
        data = {
            'exists': bool(student or teacher or teacher_email),
            'student': student,
            'teacher': teacher,
            'teacher_email': teacher_email
        }
        return Response(data=data,
                        status=status.HTTP_200_OK)


class IsLoggedInView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        student = get_current_student(request)
        classroom = get_current_classroom(request)
        if student:
            return Response({'auth': True, 'student': True, 'data': StudentSerializer(student).data},
                            status=status.HTTP_200_OK)
        if classroom:
            return Response({'auth': True, 'student': False, 'data': ClassroomSerializer(classroom).data},
                            status=status.HTTP_200_OK)
        return Response({"auth": False}, status=status.HTTP_200_OK)


class GetEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        username = request.data.get('username')
        is_student = request.data.get('is_student')
        if is_student:
            try:
                student = Student.objects.get(username=username)
                classroom = Classroom.objects.get(class_id=student.class_id)
            except (Student.DoesNotExist, Classroom.DoesNotExist):
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                classroom = Classroom.objects.get(owner=username)
            except Classroom.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'email': classroom.email}, status=status.HTTP_200_OK)


class PasswordResetView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request: Request) -> Response:
        password_reset_form = PasswordResetForm(request)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = Classroom.objects.filter(email=data)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Todos Password Reset Request"
                    email_template_name = "authentication/password/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        # must be changed for production
                        "domain": "127.0.0.1:8000",
                        "site_name": "Todos",
                        "uid": urlsafe_base64_encode(force_bytes(user.owner)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        # should change to https before production
                        "protocol": "http"
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        # Need to change the from email for production
                        send_mail(subject, email, "admin@todos.com", [user.email], fail_silently=False)
                    except BadHeaderError:
                        return Response(status=status.HTTP_400_BAD_REQUEST)
                    return redirect("/api/password_reset/done/")
        return Response(status=status.HTTP_400_BAD_REQUEST)
