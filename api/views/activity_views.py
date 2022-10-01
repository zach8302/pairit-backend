from ..models import Activity
from ..serializers import ActivitySerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response


class ActivityView(APIView):
    serializer_class = ActivitySerializer

    def post(self, request: Request) -> Response:
        queryset = Activity.objects.all()
        name: str = request.data.get("name")
        description: str = request.data.get("description")
        num: int = len(queryset)

        activity = Activity(description=description, num=num, name=name)
        serializer = self.serializer_class(instance=activity)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request) -> Response:
        data = request.data
        num: int = data['num']
        try:
            activity = Activity.objects.get(num=num)
            serializer = self.serializer_class(instance=activity, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        except Activity.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request: Request) -> Response:
        data = request.data
        num: int = data['num']
        try:
            activity = Activity.objects.get(num=num)
            serializer = self.serializer_class(instance=activity)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Activity.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request: Request) -> Response:
        data = request.data
        num: int = data['num']
        try:
            activity = Activity.objects.get(num=num)
            activity.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Activity.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
