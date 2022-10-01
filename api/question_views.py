from .serializers import QuestionsSerializer
from .models import Questions

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import JSONParser


class ListQuestionsView(generics.ListAPIView):
    queryset = Questions.objects.all()
    serializer_class = QuestionsSerializer


class QuestionsView(APIView):
    serializer_class = QuestionsSerializer

    def post(self, request: Request) -> Response:
        queryset = Questions.objects.all()
        request_data = JSONParser().parse(request)

        name: str = request_data["name"]
        questions_param: str = request_data["questions"]
        url: str = request_data["url"]
        num: int = len(queryset)
        if "num" in request_data:
            num = request_data["num"]

        questions = Questions(questions=questions_param, num=num, name=name, url=url)
        serializer = self.serializer_class(instance=questions)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request) -> Response:
        data = JSONParser().parse(request)
        num: int = data['num']
        try:
            questions = Questions.objects.get(num=num)
            serializer = self.serializer_class(instance=questions, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        except Questions.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request: Request) -> Response:
        data = JSONParser().parse(request)
        num: int = data['num']
        try:
            questions = Questions.objects.get(num=num)
            questions.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Questions.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request: Request) -> Response:
        data = JSONParser().parse(request)
        num: int = data['num']
        try:
            questions = Questions.objects.get(num=num)
            serializer = self.serializer_class(instance=questions)
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Questions.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
