from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

class LoginView(APIView):

    def post(self, request, format=None):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'Success' : "Logged in successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({'Login Failed': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)

class SignUpView(APIView):

    def post(self, request, format=None):
        username = request.data['username']
        password = request.data['password']
        user = User.objects.create_user(username=username, password=password)
        user.first_name = request.data['first_name']
        if 'email' in request.data:
            user.email = request.data['email']
        user.save()
        print(user.email)
        login(request, user)
        return Response({'Success' : "Logged in successfully"}, status=status.HTTP_200_OK)

class LogOutView(APIView):

    def post(self, request, format=None):
        logout(request)
        return Response({'Success' : "Logged out successfully"}, status=status.HTTP_200_OK)