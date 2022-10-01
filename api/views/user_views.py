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

    def get(self, request: Request) -> Response:
        student, teacher, teacher_email = None, None, None
        if 'username' in request.data:
            username = request.data.get('username')
            student = Student.objects.filter(username=username)
            teacher = Classroom.objects.filter(owner=username)
        if 'email' in request.data:
            email = request.data.get('email')
            teacher_email = Classroom.objects.filter(email=email)
        return Response(data={"exists": bool(student or teacher or teacher_email)}, status=status.HTTP_200_OK)


class IsLoggedInView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        student = get_current_student(request)
        classroom = get_current_classroom(request)
        if student:
            return Response({'auth': True, 'student': True, 'data': StudentSerializer(student).validated_data},
                            status=status.HTTP_200_OK)
        if classroom:
            return Response({'auth': True, 'student': False, 'data': ClassroomSerializer(classroom).validated_data},
                            status=status.HTTP_200_OK)
        return Response({"auth": False}, status=status.HTTP_200_OK)
