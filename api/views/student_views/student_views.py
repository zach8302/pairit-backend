from typing import Optional
from back.api.views.class_views.class_views import generate_class_partner_id
from ...services.class_services.class_services import generate_partnerships
from ...serializers import StudentSerializer, CreateStudentSerializer
from ...models import Classroom, Student
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.parsers import JSONParser
import random

def get_current_student(request : Request) -> Optional(Student):
    request_data = JSONParser().parse(request)
    if 'user' not in request_data or not 'username' not in request_data['user'] or not request_data['user']['username']:
        return None

    username = request_data['user']['username']
    try:
        return Student.objects.get(username=username)
    except Student.DoesNotExist:
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

class GetStudentPartnerView(APIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request : Request, format=None):
        current = get_current_student(request)
        partnership_id = current.partnership_id
        queryset = [s for s in Student.objects.filter(partnership_id=partnership_id) if s.class_id != current.class_id]
        if partnership_id and queryset:
            partner = queryset[0]
            return Response({'exists':True, 'data':self.serializer_class(partner).data}, status=status.HTTP_200_OK)
        else:
            return Response({'exists':False, 'data':None}, status=status.HTTP_200_OK)


class SetStudentPartnerView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, format=None):
        first_id = request.data.get("first_id")
        second_id = request.data.get("second_id")
        first = Classroom.objects.get(class_id=first_id)
        second = Classroom.objects.get(class_id=second_id)
        id = generate_class_partner_id(6)
        first.partnership_id = id
        second.partnership_id = id
        first.save()
        second.save()
        generate_partnerships(first_id, second_id)

        return Response({'success':True}, status=status.HTTP_200_OK)