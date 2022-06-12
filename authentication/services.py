from os import access
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth import authenticate, login, logout

def get_tokens(request, username, password):
    user = authenticate(request, username=username, password=password)
    refresh = TokenObtainPairSerializer().get_token(user)  
    access = AccessToken().for_user(user)
    return (refresh, access)