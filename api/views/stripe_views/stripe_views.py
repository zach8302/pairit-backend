from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from back.api.views.class_views.class_views import get_current_classroom
from ...services.services import check_sub, create_checkout_session, webhook_received
from django.utils import timezone

class IsSubscribedView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        classroom = get_current_classroom(request)
        expires = classroom.expires
        if (not expires or not timezone.now() < expires) and not check_sub(classroom.email):
            return Response({"subscribed" : False}, status=status.HTTP_200_OK)
        return Response({"subscribed" : True}, status=status.HTTP_200_OK)

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        classroom = get_current_classroom(request)
        email = classroom.email
        if not email:
            #FREAK OUT
            pass
        url = create_checkout_session(email)
        return Response({"url" : url}, status=status.HTTP_200_OK)

class StripeWebhookView(APIView):
    def post(self, request, format=None):
        ok = webhook_received(request)
        return Response({"success" : ok}, status=status.HTTP_200_OK)