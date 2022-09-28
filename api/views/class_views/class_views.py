from ...serializers import ClassroomSerializer, CreateClassroomSerializer, StudentSerializer
from ...models import Classroom, Student, Session
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from ...services.services import add_to_mailing_list, create_portal, generate_partnerships, create_sessions, loops_event
from django.utils import timezone
import random

choices = ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'M', 'P', 'Q', 'R', 'T', 'V', 'W', 'X', 'Y', '2', '3', '4', '6', '7', '8', '9']

def generate_class_id(length : int) -> str:
    id : str = ''.join(random.choices(choices, k=length))
    while Classroom.objects.filter(class_id=id):
        id = ''.join(random.choices(choices, k=length))
    return id

def generate_class_partner_id(length : int) -> str:
    id : str = ''.join(random.choices(choices, k=length))
    while Classroom.objects.filter(partnership_id=id):
        id = ''.join(random.choices(choices, k=length))
    return id

def get_current_classroom(request):
    username = request.user.username
    print(username)
    queryset = Classroom.objects.filter(owner=username)
    studentset = Student.objects.filter(username=username)
    if queryset:
        return queryset[0]
    elif studentset:
        student = studentset[0]
        classroom = Classroom.objects.get(class_id=student.class_id)
        return classroom
    else:
        return None

class ClassroomView(generics.ListAPIView):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer

class GetClassroomView(APIView):
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        classroom = get_current_classroom(request)
        if classroom:
            sessions = Session.objects.filter(class_id=classroom.partnership_id)
            data = ClassroomSerializer(classroom).data
            expires = None
            if classroom.is_ready:
                if not sessions or timezone.now() >= sessions[0].expires:
                    partners = [c for c in Classroom.objects.filter(partnership_id=classroom.partnership_id) if c.class_id != classroom.class_id]
                    if partners and partners[0].is_ready:
                        classroom.is_ready = False
                        partners[0].is_ready = False
                        classroom.num_calls += 1
                        partners[0].num_calls += 1
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
            email = request.data.get('email')
            add_to_mailing_list(email, first)
            loops_event(email, "Sign up")
            classroom = Classroom(name=name, owner=owner, first=first, email=email)
            classroom.class_id=generate_class_id(6)
            classroom.save()
            return Response(ClassroomSerializer(classroom).data, status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)

class ClassroomExistsView(APIView): 
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        class_id = request.data.get('class_id')
        norm = class_id.upper()
        queryset = Classroom.objects.filter(class_id=norm)
        return Response({"exists" : (bool(queryset))})

class SetReadyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):  
        print(request.user.username)
        current = get_current_classroom(request)
        if not current:
            return Response({"ready" : False, "active" : False})
        partnership_id = current.partnership_id
        queryset = [c for c in Classroom.objects.filter(partnership_id=partnership_id) if c.owner != current.owner]
        current.is_ready = not current.is_ready
        ready = False
        if current.is_ready and partnership_id and queryset:
            partner = queryset[0]
            if partner.is_ready:
                ready=True
                for s in Session.objects.filter(class_id=partnership_id):
                    s.delete()
                generate_partnerships(current.class_id, partner.class_id)
                try:
                    create_sessions(partner.class_id, partnership_id)
                except Exception as e:
                    print(e)
                    return Response({"ready" : current.is_ready, "active" : current.is_ready and ready})
        current.save()
        return Response({"ready" : current.is_ready, "active" : current.is_ready and ready})

class CreatePortalView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        classroom = get_current_classroom(request)
        email = classroom.email
        if not email:
            #FREAK OUT
            pass
        url = create_portal(email)
        return Response({"url" : url}, status=status.HTTP_200_OK)

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