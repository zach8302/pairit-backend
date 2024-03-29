from rest_framework import serializers
from .models import Activity, Classroom, Student, Session, Questions


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('username', 'class_id', 'personality', 'partnership_id', 'first', 'image', 'display_name')


class CreateStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('class_id', 'personality', 'first', 'username', 'display_name')


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ('owner', 'class_id', 'name', 'first', 'partnership_id', 'is_ready', 'num_calls', 'email', 'expires',
                  'display_name')


class CreateClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ('name', 'owner', 'first', 'email', 'display_name')


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ('partnership_id', 'session_id', 'active', 'expires', 'token')


class QuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = ("name", "questions", "num", "url")


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ("name", "description", "num")
