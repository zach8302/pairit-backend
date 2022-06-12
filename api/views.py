from http.client import HTTPResponse
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .serializers import ClassroomSerializer, StudentSerializer, CreateClassroomSerializer, CreateStudentSerializer, SessionSerializer
from .models import Classroom, Student, Session
from rest_framework import generics, serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .services import generate_parnterships, create_sessions
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

import random
import string

def generate_class_id(length):
    id = ''.join(random.choices(string.ascii_uppercase, k=length))
    while Classroom.objects.filter(class_id=id):
        id = ''.join(random.choices(string.ascii_uppercase, k=length))
    return id

def generate_class_partner_id(length):
    id = ''.join(random.choices(string.ascii_uppercase, k=length))
    while Classroom.objects.filter(partnership_id=id):
        id = ''.join(random.choices(string.ascii_uppercase, k=length))
    return id

def get_current_student(request):
    username = request.user.username
    queryset = Student.objects.filter(username=username)
    if queryset:
        return queryset[0]
    else:
        return None

def get_current_classroom(request):
    username = request.user.username
    queryset = Classroom.objects.filter(owner=username)
    if queryset:
        return queryset[0]
    else:
        return None

def delete_sessions():
    sessions = Session.objects.all()
    for s in sessions:
        s.delete()

class StudentView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class ClassroomView(generics.ListAPIView):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer

class SessionView(generics.ListAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

class GetStudentView(APIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

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
            class_id = serializer.data.get('class_id')
            personality = request.data.get('personality')
            first = request.data.get('first')
            queryset = Student.objects.filter(username=username)
            classset = Classroom.objects.filter(class_id=class_id)
            if not classset.exists():
                return Response({'Bad Request': 'Invalid class id'}, status=status.HTTP_400_BAD_REQUEST)
            elif queryset.exists():
                return Response({'Bad Request': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                student = Student(username=username, class_id=class_id, personality=personality, first=first)
                student.save()
                return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

class GetClassroomView(APIView):
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        username = request.user.username
        queryset = Classroom.objects.filter(owner=username)
        if queryset.exists():
            classroom = queryset[0]
            sessions = Session.objects.filter(class_id=classroom.partnership_id)
            data = ClassroomSerializer(classroom).data
            expires = None
            if classroom.is_ready and sessions:
                if timezone.now() >= sessions[0].expires:
                    partners = [c for c in Classroom.objects.filter(partnership_id=classroom.partnership_id) if c.class_id != classroom.class_id]
                    if partners and partners[0].is_ready:
                        classroom.is_ready = False
                        partners[0].is_ready = False
                        classroom.save()
                        partners[0].save()
                else:
                    seconds = (sessions[0].expires - timezone.now()).total_seconds()
                    expires = int(seconds/60) + 1
            data["expires"] = expires
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'Bad Request': 'Class does not exist'}, status=status.HTTP_400_BAD_REQUEST)

class CreateClassroomView(APIView):
    serializer_class = CreateClassroomSerializer
    permission_classes = [AllowAny]


    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            name=serializer.data.get('name')
            owner=serializer.data.get('owner')
            first = request.data.get('first')
            classroom = Classroom(name=name, owner=owner, first=first)
            classroom.class_id=generate_class_id(6)
            classroom.save()
            return Response(ClassroomSerializer(classroom).data, status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)

class MyStudentsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentSerializer

    def get(self, request, format=None):
        username = request.user.username
        classroom = Classroom.objects.filter(owner=username)[0]
        queryset = Student.objects.filter(class_id=classroom.class_id)
        if queryset:
            students = [StudentSerializer(student).data for student in queryset]
            return Response({'students' : students}, status=status.HTTP_200_OK)
        else:
            return Response({'students':[]}, status=status.HTTP_200_OK)
        
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

class IsStudentView(APIView):
    def get(self, request, format=None):
        username = request.user.username
        queryset = Student.objects.filter(username=username)
        return Response({"student" : (bool(queryset))})

class ClassroomExistsView(APIView): 
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        class_id = request.data.get('class_id')
        queryset = Classroom.objects.filter(class_id=class_id)
        return Response({"exists" : (bool(queryset))})

class UserExistsView(APIView): 
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        username = request.data.get('username')
        student = Student.objects.filter(username=username)
        teacher = Classroom.objects.filter(owner=username)
        return Response({"exists" : student.exists() or teacher.exists()})

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

class GetPartnerClassView(APIView):
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        current = get_current_classroom(request)
        partnership_id = current.partnership_id
        queryset = [c for c in Classroom.objects.filter(partnership_id=partnership_id) if c.class_id != current.class_id]
        if partnership_id and queryset:
            partner = queryset[0]
            return Response({'exists':True, 'data':self.serializer_class(partner).data}, status=status.HTTP_200_OK)
        else:
            return Response({'exists':False, 'data':None}, status=status.HTTP_200_OK)

class GetPartnerView(APIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        current = get_current_student(request)
        partnership_id = current.partnership_id
        queryset = [s for s in Student.objects.filter(partnership_id=partnership_id) if s.username != current.username]
        if partnership_id and queryset:
            partner = queryset[0]
            return Response({'exists':True, 'data':self.serializer_class(partner).data}, status=status.HTTP_200_OK)
        else:
            return Response({'exists':False, 'data':None}, status=status.HTTP_200_OK)

class GetSessionView(APIView):
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        current = get_current_student(request)
        partnership_id = current.partnership_id
        queryset = Session.objects.filter(partnership_id=partnership_id)
        if partnership_id and queryset and timezone.now() < queryset[0].expires:
            session = queryset[0]
            return Response({'exists':True, 'data':self.serializer_class(session).data}, status=status.HTTP_200_OK)
        else:
            return Response({'exists':False, 'data':None}, status=status.HTTP_200_OK)

class SetPartnerView(APIView):
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
        generate_parnterships(first_id, second_id)

        return Response({'success':True}, status=status.HTTP_200_OK)

class SetReadyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):  
        current = get_current_classroom(request)
        partnership_id = current.partnership_id
        queryset = [c for c in Classroom.objects.filter(partnership_id=partnership_id) if c.owner != current.owner]
        current.is_ready = not current.is_ready
        current.save()
        ready = False
        if current.is_ready and partnership_id and queryset:
            partner = queryset[0]
            if partner.is_ready:
                ready=True
                for s in Session.objects.filter(class_id=partnership_id):
                    s.delete()
                create_sessions(partner.class_id, partnership_id)
        return Response({"ready" : current.is_ready, "active" : current.is_ready and ready})

class ResetSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):  
        queryset = Session.objects.all()
        for s in queryset:
            s.delete()
        queryset = Classroom.objects.all()
        for c in queryset:
            c.is_ready = False
            c.save()
        
