from ..serializers import QuestionsSerializer
from ..models import Questions

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response


class ListQuestionsView(generics.ListAPIView):
    queryset = Questions.objects.all()
    serializer_class = QuestionsSerializer


class QuestionsView(APIView):
    serializer_class = QuestionsSerializer

    def post(self, request: Request) -> Response:
        queryset = Questions.objects.all()

        name: str = request.data.get("name")
        questions_param: str = request.data.get("questions")
        url: str = request.data.get("url")
        num: int = len(queryset)
        if "num" in request.data:
            num = request.data.get("num")

        questions = Questions(questions=questions_param, num=num, name=name, url=url)
        serializer = self.serializer_class(instance=questions)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request) -> Response:
        num: int = request.data.get('num')
        try:
            questions = Questions.objects.get(num=num)
            serializer = self.serializer_class(instance=questions, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)
        except Questions.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request: Request) -> Response:
        num: int = request.data.get('num')
        try:
            questions = Questions.objects.get(num=num)
            questions.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Questions.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request: Request) -> Response:
        num: int = request.data.get('num')
        try:
            questions = Questions.objects.get(num=num)
            serializer = self.serializer_class(instance=questions)
            if serializer.is_valid():
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Questions.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
