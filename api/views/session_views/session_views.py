from back.api.services.services import validate_session
from back.api.views.class_views.class_views import get_current_classroom
from back.api.views.student_views.student_views import get_current_student
from ...serializers import SessionSerializer
from ...models import Classroom, Session, Questions
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

def delete_sessions():
    sessions = Session.objects.all()
    for s in sessions:
        s.delete()

class SessionView(generics.ListAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

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
        return Response({'success':True}, status=status.HTTP_200_OK)

class ValidateSessionView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        classroom = get_current_classroom(request)
        email = classroom.email
        id = request.data.get("session_id")
        ok = validate_session(id, email)
        return Response({"success" : ok}, status=status.HTTP_200_OK)