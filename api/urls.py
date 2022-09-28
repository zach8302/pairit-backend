from django.urls import path

from back.api.views.student_views.student_views import *
from back.api.views.class_views.class_views import *
from back.api.views.partner_views.partner_views import *
from back.api.views.question_views.question_views import *
from back.api.views.session_views.session_views import *
from back.api.views.user_views.user_views import *
from back.api.views.activity_views.activity_views import *
from back.api.views.stripe_views.stripe_views import *

urlpatterns = [
    # student urls
    path('students', StudentView.as_view()),
    path('create-student', CreateStudentView.as_view()),
    path('get-student', GetStudentView.as_view()),
    path('complete-form', CompleteFormView.as_view()),
    path('is-student', IsStudentView.as_view()),
    
    # class urls
    path('classes', ClassroomView.as_view()),
    path('create-class', CreateClassroomView.as_view()),
    path('get-classroom', GetClassroomView.as_view()),
    path('class-exists', ClassroomExistsView.as_view()),
    path('my-students', MyStudentsView.as_view()),
    path('set-ready', SetReadyView.as_view()),

    # partner urls
    path('get-partner-classroom', GetPartnerClassView.as_view()),
    path('create-partnership', SetPartnerView.as_view()),
    path('get-partner', GetPartnerView.as_view()),

    # question urls
    path('questions', QuestionsView.as_view()),
    path('set-questions', SetQuestionsView.as_view()),
    path('get-questions', GetQuestionsView.as_view()),
    path('delete-questions', DeleteQuestionsView.as_view()),

    # session urls
    path('sessions', SessionView.as_view()),
    path('get-session', GetSessionView.as_view()),
    path('is-logged-in', IsLoggedInView.as_view()),
    path('reset-sessions', ResetSessionsView.as_view()),
    path('validate-session', ValidateSessionView.as_view()),
    path('create-portal', CreatePortalView.as_view()),

    # user urls
    path('user-exists', UserExistsView.as_view()),

    # activity urls
    path('create-activity', CreateActivityView.as_view()),
    path('get-activity', GetActivityView.as_view()),

    # stripe urls
    path('is-subscribed', IsSubscribedView.as_view()),
    path('checkout', CheckoutView.as_view()),
    path('stripe-webhooks', StripeWebhookView.as_view()),
]