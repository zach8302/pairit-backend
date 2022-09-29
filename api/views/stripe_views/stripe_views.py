from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from back.api.services.stripe_services.stripe_services import create_portal

from back.api.views.class_views.class_views import get_current_classroom
from ...services.class_services.class_services import check_sub, create_checkout_session, webhook_received, validate_session
from django.utils import timezone

class IsSubscribedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request : Request, format=None) -> Response:
        classroom = get_current_classroom(request)
        if not classroom:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        expires = classroom.expires
        if (not expires or timezone.now() > expires) and not check_sub(classroom.email):
            return Response({"subscribed" : False}, status=status.HTTP_200_OK)
        return Response({"subscribed" : True}, status=status.HTTP_200_OK)

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request : Request, format=None) -> Response:
        classroom = get_current_classroom(request)
        if not classroom:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        email = classroom.email
        if not email:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        url = create_checkout_session(email)
        return Response({"url" : url}, status=status.HTTP_200_OK)

class StripeWebhookView(APIView):
    def post(self, request : Request, format=None) -> Response:
        ok = webhook_received(request)
        return Response({"success" : ok}, status=status.HTTP_200_OK)

class ValidateSessionView(APIView):
    def post(self, request : Request, format=None) -> Response:
        classroom = get_current_classroom(request)
        if not classroom:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        email = classroom.email
        id = request.data.get("session_id")
        if not email or not id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ok = validate_session(id, email)
        return Response({"success" : ok}, status=status.HTTP_200_OK)

class CreatePortalView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request : Request, format=None):
        classroom = get_current_classroom(request)
        if not classroom:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        email = classroom.email
        if not email:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        url = create_portal(email)
        return Response(data={"url" : url}, status=status.HTTP_200_OK)