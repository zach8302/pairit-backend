from back.api.views.class_views.class_views import get_current_classroom
from back.api.views.student_views.student_views import get_current_student
from ...serializers import ClassroomSerializer, StudentSerializer
from ...models import Classroom, Student, Questions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class UserExistsView(APIView): 
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        student, teacher, teacher_email = None, None, None
        if 'username' in request.data:
            username = request.data.get('username')
            student = Student.objects.filter(username=username)
            teacher = Classroom.objects.filter(owner=username)
        if 'email' in request.data:
            email = request.data.get('email')
            teacher_email = Classroom.objects.filter(email=email)
        return Response({"exists" : bool(student or teacher or teacher_email)})

class IsLoggedInView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        if not request.user:
            return Response({"auth" : False}, status=status.HTTP_200_OK)
        student = get_current_student(request)
        classroom = get_current_classroom(request)
        if student:
            return Response({'auth':True, 'student':True, 'data':StudentSerializer(student).data}, status=status.HTTP_200_OK)
        if classroom:
            return Response({'auth':True, 'student':False, 'data':ClassroomSerializer(classroom).data}, status=status.HTTP_200_OK)
        return Response({"auth" : False}, status=status.HTTP_200_OK)