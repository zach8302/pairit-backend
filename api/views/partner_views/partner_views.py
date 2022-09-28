from back.api.views.class_views.class_views import generate_class_partner_id, get_current_classroom
from back.api.views.student_views.student_views import get_current_student
from ...serializers import ClassroomSerializer, StudentSerializer
from ...models import Classroom, Student
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from ...services.services import generate_partnerships

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
        queryset = [s for s in Student.objects.filter(partnership_id=partnership_id) if s.class_id != current.class_id]
        if partnership_id and queryset:
            partner = queryset[0]
            return Response({'exists':True, 'data':self.serializer_class(partner).data}, status=status.HTTP_200_OK)
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
        generate_partnerships(first_id, second_id)

        return Response({'success':True}, status=status.HTTP_200_OK)