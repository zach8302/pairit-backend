from typing import Optional
import random

from .class_views import generate_class_partner_id
from .services.class_services.class_services import generate_partnerships
from .serializers import StudentSerializer, CreateStudentSerializer, ClassroomSerializer
from .models import Classroom, Student

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.parsers import JSONParser


def get_current_student(request: Request) -> Optional[Student]:
    request_data = JSONParser().parse(request)
    if 'user' not in request_data or not 'username' not in request_data['user'] or not request_data['user']['username']:
        return None

    username = request_data['user']['username']
    try:
        return Student.objects.get(username=username)
    except Student.DoesNotExist:
        return None


class IsStudentView(APIView):
    def get(self, request: Request) -> Response:
        student = get_current_student(request)
        return Response(data={"student": (bool(student))}, status=status.HTTP_200_OK)


class ListStudentView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        student = get_current_student(request)
        if student:
            return Response(data=StudentSerializer(instance=student).data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request: Request) -> Response:
        request_data = JSONParser().parse(request)
        serializer = CreateStudentSerializer(data=request_data)

        if serializer.is_valid():
            username = request_data['username']
            class_id = request_data['class_id'].upper()
            personality = request_data['personality']
            first = request_data['first']

            try:
                classroom = Classroom.objects.get(class_id=class_id)
                student = Student(username=username, class_id=class_id, personality=personality, first=first,
                                  image=random.randrange(21))
                queryset = Student.objects.filter(username=username)
                if queryset.exists():
                    return Response({'Bad Request': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
                student_serializer = StudentSerializer(instance=student)
                return Response(student_serializer.data, status=status.HTTP_201_CREATED)
            except Classroom.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class CompleteFormView(APIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        request_data = JSONParser().parse(request)
        personality = request_data['personality']
        student = get_current_student(request=request)
        if student:
            serializer = self.serializer_class(instance=student)
            serializer.data['personality'] = personality
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Bad Request': 'Student does not exist'}, status=status.HTTP_400_BAD_REQUEST)


class GetStudentPartnerView(APIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        student = get_current_student(request)
        if not student:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        partnership_id = student.partnership_id
        if not partnership_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        queryset = [s for s in Student.objects.filter(partnership_id=partnership_id) if s.class_id != student.class_id]
        if not queryset:
            return Response({'exists': False, 'data': None}, status=status.HTTP_200_OK)
        partner = queryset[0]
        return Response({'exists': True, 'data': self.serializer_class(instance=partner).data},
                        status=status.HTTP_200_OK)


class SetStudentPartnerView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request: Request) -> Response:
        request_data = JSONParser().parse(request)

        first_id = request_data['first_id']
        second_id = request_data['second_id']
        try:
            first = Classroom.objects.get(class_id=first_id)
            first_serializer = ClassroomSerializer(instance=first)
            second = Classroom.objects.get(class_id=second_id)
            second_serializer = ClassroomSerializer(instance=second)
        except Classroom.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        partner_id = generate_class_partner_id(6)
        first_serializer.data['partner_id'] = partner_id
        second_serializer.data['partner_id'] = partner_id
        if first_serializer.is_valid() and second_serializer.is_valid():
            first_serializer.save()
            second_serializer.save()
            generate_partnerships(first_id, second_id)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_417_EXPECTATION_FAILED)