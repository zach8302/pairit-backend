from ...serializers import QuestionsSerializer
from ...models import Questions, Questions
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

class QuestionsView(generics.ListAPIView):
    queryset = Questions.objects.all()
    serializer_class = QuestionsSerializer

class SetQuestionsView(APIView):
    def post(self, request, format=None):
        queryset = Questions.objects.all()
        print(request.data)
        name = request.data.get("name")
        questions = request.data.get("questions")
        url = request.data.get("url")
        num = len(queryset)
        if "num" in request.data:
            num = request.data.get("num")
        print(name, questions, num, url)
        questions = Questions(questions=questions, num=num, name=name, url=url)
        print(questions.questions, questions.num, questions.name, questions.url)
        questions.save()
        return Response({'success':True}, status=status.HTTP_201_CREATED)

class GetQuestionsView(APIView):
    def post(self, request, format=None):
        num = request.data.get("num")
        queryset = Questions.objects.filter(num=num)
        if queryset:
            question = queryset[0]
            print(question)
            return Response({"name" : question.name, "questions" : question.questions, "url" : question.url}, status=status.HTTP_200_OK)
        else:
            return Response({"Status" : "Not Found"}, status=status.HTTP_404_NOT_FOUND)

class DeleteQuestionsView(APIView):
    def post(self, request, format=None):
        num = request.data.get("num")
        queryset = Questions.objects.filter(num=num)
        queryset.delete()
        return Response({'Status': 'success'}, status=status.HTTP_200_OK)