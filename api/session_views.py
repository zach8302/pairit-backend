from student_views import get_current_student
from serializers import SessionSerializer
from models import Classroom, Session

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone


class ListSessionView(generics.ListAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class SessionView(APIView):
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        current = get_current_student(request)
        if not current:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        partnership_id = current.partnership_id
        if not partnership_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            session = Session.objects.filter(partnership_id=partnership_id)
            serializer = self.serializer_class(instance=session)
            serializer_data = serializer.data
            if serializer.is_valid() and timezone.now() < session.expires:
                return Response(data=serializer_data, status=status.HTTP_200_OK)
        except Session.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request: Request) -> Response:
        queryset = Session.objects.all()
        for s in queryset:
            s.delete()
        queryset = Classroom.objects.all()
        for c in queryset:
            c.is_ready = False
            c.save()
        return Response(status=status.HTTP_200_OK)
