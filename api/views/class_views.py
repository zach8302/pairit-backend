import datetime
from typing import Optional
import random

from ..services.session_services.session_services import create_session_data
from ..serializers import ClassroomSerializer, CreateClassroomSerializer, StudentSerializer
from ..models import Classroom, Student, Session
from ..services.class_services.class_services import generate_partnerships
from ..services.loops_services.loops_services import add_to_mailing_list, loops_event

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone

CALL_LENGTH = 15
choices = ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'M', 'P', 'Q', 'R', 'T', 'V', 'W', 'X', 'Y', '2', '3', '4', '6', '7', '8',
           '9']


# generates session keys and associates each one with a partnership
def create_sessions(class_id, id):
    students = Student.objects.filter(class_id=class_id)
    seen = set()
    for s in students:
        partner = s.partnership_id
        if partner not in seen:
            data = create_session_data()
            session_id = data['session_id']
            token = data['token']
            expires = datetime.datetime.now() + datetime.timedelta(minutes=CALL_LENGTH)
            session = Session(partnership_id=partner, class_id=id, session_id=session_id, token=token, expires=expires)
            seen.add(partner)
            session.save()


def generate_class_id(length: int) -> str:
    class_id: str = ''.join(random.choices(choices, k=length))
    while Classroom.objects.filter(class_id=class_id):
        class_id = ''.join(random.choices(choices, k=length))
    return class_id


def generate_class_partner_id(length: int) -> str:
    class_partner_id: str = ''.join(random.choices(choices, k=length))
    while Classroom.objects.filter(partnership_id=class_partner_id):
        class_partner_id = ''.join(random.choices(choices, k=length))
    return class_partner_id


def get_current_classroom(request: Request) -> Optional[Classroom]:
    username: str = request.user.username
    try:
        return Classroom.objects.get(owner=username)
    except Classroom.DoesNotExist:
        try:
            student = Student.objects.get(username=username)
            return Classroom.objects.get(class_id=student.class_id)
        except (Classroom.DoesNotExist, Student.DoesNotExist):
            return None


def get_class_partner(partnership_id: str, class_id: str) -> Optional[Classroom]:
    # class_id is the id of the current class, need to ignore to not return own class as partner
    partners = [c for c in Classroom.objects.filter(partnership_id=partnership_id) if c.class_id != class_id]
    if partners:
        return partners[0]
    return None


class ListClassroomView(generics.ListAPIView):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer


class GetClassroomView(APIView):
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        classroom = get_current_classroom(request)
        if classroom is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        class_data = ClassroomSerializer(instance=classroom).validated_data

        class_id = class_data['class_id']
        partnership_id = class_data['partnership_id']
        sessions = Session.objects.filter(class_id=partnership_id)
        expires = None
        ready = class_data['is_ready']

        # this is cleanup stuff, maybe move this later
        if ready:
            if not sessions or timezone.now() >= sessions[0].expires:

                partner = get_class_partner(partnership_id=partnership_id, class_id=class_id)

                if not partner:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

                partner_data = ClassroomSerializer(instance=partner).data

                if partner_data['is_ready']:
                    partner_data['is_ready'] = False
                    class_data['num_calls'] += 1
                    partner_data['num_calls'] += 1
                    ClassroomSerializer(instance=classroom, data=class_data).save()
                    ClassroomSerializer(instance=partner, data=partner_data).save()
            else:
                seconds = (sessions[0].expires - timezone.now()).total_seconds()
                expires = int(seconds / 60) + 1
        class_data['expires'] = expires
        ClassroomSerializer(instance=classroom, data=class_data).save()
        return Response(class_data, status=status.HTTP_200_OK)


class SetReadyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        classroom = get_current_classroom(request)
        if not classroom:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ClassroomSerializer(instance=classroom)
        class_data = serializer.validated_data
        class_id = class_data['class_id']
        partnership_id = class_data['partnership_id']
        partner = get_class_partner(partnership_id=partnership_id, class_id=class_id)

        class_ready = class_data['is_ready']
        class_ready = not class_ready

        if not class_ready:
            return Response(data={"ready": class_ready}, status=status.HTTP_400_BAD_REQUEST)
        elif not partnership_id:
            return Response(data={"partnership_id": None}, status=status.HTTP_400_BAD_REQUEST)
        elif not partner:
            return Response(data={"partner": None}, status=status.HTTP_400_BAD_REQUEST)

        if partner.is_ready:
            # Old cleanup, should be moved eventually
            for s in Session.objects.filter(class_id=partnership_id):
                s.delete()
            generate_partnerships(class_id, partner.class_id)
            try:
                create_sessions(partner.class_id, partnership_id)
            except Exception as e:
                return Response({"ready": class_ready, "active": class_ready and partner.is_ready},
                                status=status.HTTP_417_EXPECTATION_FAILED)
        return Response({"ready": class_ready, "active": class_ready and partner.is_ready},
                        status=status.HTTP_200_OK)


class ClassroomExistsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        if 'class_id' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        class_id = request.data.get('class_id')
        norm = class_id.upper()
        try:
            classroom = Classroom.objects.get(class_id=norm)
            return Response({"exists": True}, status=status.HTTP_200_OK)
        except Classroom.DoesNotExist:
            return Response({"exists": False}, status=status.HTTP_200_OK)


class CreateClassroomView(APIView):
    serializer_class = CreateClassroomSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        first: str = serializer.validated_data['first']
        email: str = serializer.validated_data['email']

        add_to_mailing_list(email, first)
        loops_event(email, "Sign up")

        serializer.validated_data['class_id'] = generate_class_id(6)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


class MyStudentsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentSerializer

    def get(self, request: Request) -> Response:
        username: str = request.user.username
        try:
            classroom = Classroom.objects.get(owner=username)
            class_id = classroom.class_id
            queryset = Student.objects.filter(class_id=class_id)
            students = [StudentSerializer(instance=student).validated_data for student in queryset]
            return Response({'students': students}, status=status.HTTP_200_OK)
        except Classroom.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetPartnerClassView(APIView):
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        current = get_current_classroom(request)
        if not current:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        class_id = current.class_id
        partnership_id = current.partnership_id
        partner = get_class_partner(partnership_id, class_id)
        if not partnership_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif not partner:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(data=self.serializer_class(instance=partner).data, status=status.HTTP_200_OK)
