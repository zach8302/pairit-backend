from typing import Optional
import random

from .class_views import generate_class_partner_id
from ..services.class_services.class_services import generate_partnerships
from ..serializers import StudentSerializer, CreateStudentSerializer, ClassroomSerializer
from ..models import Classroom, Student

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser


def get_current_student(request: Request) -> Optional[Student]:
    username = request.user.username
    try:
        return Student.objects.get(username=username)
    except Student.DoesNotExist:
        return None


class IsStudentView(APIView):
    def post(self, request: Request) -> Response:
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
        serializer = CreateStudentSerializer(data=request.data)
        if serializer.is_valid():
            username = request.data.get('username')
            class_id = request.data.get('class_id').upper()
            personality = request.data.get('personality')
            first = request.data.get('first')
            display_name = request.data.get('display_name')
            try:
                classroom = Classroom.objects.get(class_id=class_id)
                student = Student(username=username, class_id=class_id, personality=personality, first=first,
                                  image=random.randrange(21), display_name=display_name)
                queryset = Student.objects.filter(username=username)
                if queryset.exists():
                    return Response({'Bad Request': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
                student.save()
                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
            except Classroom.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class CompleteFormView(APIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        personality = request.data.get('personality')
        student = get_current_student(request=request)
        if student:
            student.personality = personality
            student.save()
            return Response(status=status.HTTP_200_OK)
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

        first_id = request.data.get('first_id')
        second_id = request.data.get('second_id')
        try:
            first: Classroom = Classroom.objects.get(class_id=first_id)
            second: Classroom = Classroom.objects.get(class_id=second_id)
        except Classroom.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        partner_id = generate_class_partner_id(6)
        first.partnership_id = partner_id
        second.partnership_id = partner_id
        first.save()
        second.save()
        generate_partnerships(first_id, second_id)
        return Response(status=status.HTTP_200_OK)