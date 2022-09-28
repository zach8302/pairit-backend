from back.api.views.class_views.class_views import get_current_classroom
from ...serializers import StudentSerializer, CreateStudentSerializer
from ...models import Classroom, Student
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import random

def get_current_student(request):
    username = request.user.username
    queryset = Student.objects.filter(username=username)
    if queryset:
        return queryset[0]
    else:
        return None

def get_student_or_classroom(request):
    student = get_current_student(request)
    classroom = get_current_classroom(request)
    if student:
        return student
    elif classroom:
        return classroom
    else:
        return None

class IsStudentView(APIView):
    def get(self, request, format=None):
        username = request.user.username
        queryset = Student.objects.filter(username=username)
        return Response({"student" : (bool(queryset))})
        
class StudentView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class GetStudentView(APIView):
    serializer_class = StudentSerializer

    def get(self, request, format=None):
        username = request.user.username
        queryset = Student.objects.filter(username=username)
        if queryset.exists():
            return Response(StudentSerializer(queryset[0]).data, status=status.HTTP_200_OK)
        else:
            return Response({'Bad Request': 'Student does not exist'}, status=status.HTTP_400_BAD_REQUEST)

class CreateStudentView(APIView):
    serializer_class = CreateStudentSerializer
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = request.data.get('username')
            class_id = serializer.data.get('class_id').upper()
            personality = request.data.get('personality')
            first = request.data.get('first')
            queryset = Student.objects.filter(username=username)
            classset = Classroom.objects.filter(class_id=class_id)
            if not classset.exists():
                return Response({'Bad Request': 'Invalid class id'}, status=status.HTTP_400_BAD_REQUEST)
            elif queryset.exists():
                return Response({'Bad Request': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                student = Student(username=username, class_id=class_id, personality=personality, first=first, image=random.randrange(21))
                student.save()
                return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

class CompleteFormView(APIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        username = request.data.get('username')
        personality = request.data.get('personality')
        queryset = Student.objects.filter(username=username)
        if queryset.exists():
            student = queryset[0]
            student.personality = personality
            student.save()
            return Response(self.serializer_class(student).data, status=status.HTTP_200_OK)
        else:
            return Response({'Bad Request': 'Student does not exist'}, status=status.HTTP_400_BAD_REQUEST)