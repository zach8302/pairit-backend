from urllib.request import Request

from back.api.serializers import ActivitySerializer
from ...models import Activity
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

class CreateActivityView(APIView):
    def post(self, request : Request, format=None) -> Response:
        queryset = Activity.objects.all()
        name : str = request.data.get("name")
        description : str = request.data.get("description")
        num : int = len(queryset)

        activity = Activity(description=description, num=num, name=name)
        activity_serializer = ActivitySerializer(instance=activity)
        if activity_serializer.is_valid:
            activity_serializer.save()
            return Response({'success' : True}, status=status.HTTP_201_CREATED)
        return Response({'success' : False}, status=status.HTTP_400_BAD_REQUEST)

class GetActivityView(APIView):
    def get(self, request : Request, format=None) -> Response:
        num : int = request.data.get("num")
        queryset = Activity.objects.filter(num=num)

        if queryset:
            activity_serializer = ActivitySerializer(queryset[0])
            return Response(activity_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"Status" : "Not Found"}, status=status.HTTP_404_NOT_FOUND)