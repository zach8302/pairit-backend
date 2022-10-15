from django.urls import path
from django.contrib.auth import views as auth_views
from .views.student_views import *
from .views.class_views import *
from .views.question_views import *
from .views.session_views import *
from .views.user_views import *
from .views.activity_views import *
from .views.stripe_views import *

urlpatterns = [
    # student urls
    path('list-students', ListStudentView.as_view()),
    path('student', StudentView.as_view()),
    path('complete-form', CompleteFormView.as_view()),
    path('is-student', IsStudentView.as_view()),
    path('create-partner', SetStudentPartnerView.as_view()),
    path('get-partner', GetStudentPartnerView.as_view()),
    
    # class urls
    path('list-classes', ListClassroomView.as_view()),
    path('create-class', CreateClassroomView.as_view()),
    path('get-class', GetClassroomView.as_view()),
    path('my-students', MyStudentsView.as_view()),
    path('set-ready', SetReadyView.as_view()),
    path('get-partner-class', GetPartnerClassView.as_view()),
    path('class-exists', ClassroomExistsView.as_view()),

    # question urls
    path('list-questions', ListQuestionsView.as_view()),
    path('questions', QuestionsView.as_view()),

    # session urls
    path('list-sessions', ListSessionView.as_view()),
    path('session', SessionView.as_view()),

    # user urls
    path('user-exists', UserExistsView.as_view()),
    path('is-logged-in', IsLoggedInView.as_view()),
    path('get-email', GetEmailView.as_view()),
    path('password_reset/', PasswordResetView.as_view()),
    path('password_reset/done', auth_views.PasswordResetDoneView.as_view()),
    path('password_reset/complete', auth_views.PasswordResetCompleteView.as_view()),
    path('password_reset/confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view()),

    # activity urls
    path('activity', ActivityView.as_view()),

    # stripe urls
    path('is-subscribed', IsSubscribedView.as_view()),
    path('checkout', CheckoutView.as_view()),
    path('stripe-webhooks', StripeWebhookView.as_view()),
    path('validate-session', ValidateSessionView.as_view()),
    path('create-portal', CreatePortalView.as_view()),
]
