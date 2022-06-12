from django.urls import path
from .views import *

urlpatterns = [
    path('students', StudentView.as_view()),
    path('create-student', CreateStudentView.as_view()),
    path('create-class', CreateClassroomView.as_view()),
    path('classes', ClassroomView.as_view()),
    path('sessions', SessionView.as_view()),
    path('get-student', GetStudentView.as_view()),
    path('get-classroom', GetClassroomView.as_view()),
    path('get-session', GetSessionView.as_view()),
    path('complete-form', CompleteFormView.as_view()),
    path('is-student', IsStudentView.as_view()),
    path('class-exists', ClassroomExistsView.as_view()),
    path('user-exists', UserExistsView.as_view()),
    path('is-logged-in', IsLoggedInView.as_view()),
    path('my-students', MyStudentsView.as_view()),
    path('get-partner-classroom', GetPartnerClassView.as_view()),
    path('create-partnership', SetPartnerView.as_view()),
    path('get-partner', GetPartnerView.as_view()),
    path('set-ready', SetReadyView.as_view()),
    path('reset-sessions', ResetSessionsView.as_view()),
]