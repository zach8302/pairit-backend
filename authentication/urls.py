from django.urls import path
from django.contrib.auth import views as auth_views
from .views import LoginView, SignUpView, LogOutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('login', LoginView.as_view()),
    path('signup', SignUpView.as_view()),
    path('logout', LogOutView.as_view()),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]