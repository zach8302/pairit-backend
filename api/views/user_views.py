from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt

from .class_views import get_current_classroom
from .student_views import get_current_student
from ..serializers import ClassroomSerializer, StudentSerializer
from ..models import Classroom, Student

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from random import choices


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
    @csrf_exempt
    def post(self, request: Request) -> Response:
        email = request.data.get('email')
        associated_users = Classroom.objects.filter(email=email)
        if associated_users.exists():
            for user in associated_users:
                subject = "Todos Password Reset Request"
                email_template_name = "authentication/password/password_reset_email.txt"
                options = [str(i) for i in range(10)]
                pin = ''.join(choices(options, k=6))
                user.pin = pin
                user.save()
                c = {
                    "email": user.email,
                    # must be changed for production
                    "domain": "127.0.0.1:8000",
                    "site_name": "Todos",
                    "uid": urlsafe_base64_encode(force_bytes(user.owner)),
                    "user": user,
                    "pin": pin,
                    # should change to https before production
                    "protocol": "http"
                }
                email = render_to_string(email_template_name, c)
                try:
                    # Need to change the from email for production
                    send_mail(subject, email, "admin@todos.com", [user.email], fail_silently=False)
                except BadHeaderError:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PasswordResetPinView(APIView):
    def post(self, request: Request) -> Response:
        pin = request.data.get('pin')
        username = request.data.get('username')
        if not pin or not username:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = Classroom.objects.get(owner=username, pin=pin)
            user.pin = None
            user.save()
            return Response(status.HTTP_200_OK)
        except Classroom.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
