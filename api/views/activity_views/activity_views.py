from email.policy import HTTP
from urllib.request import Request

from back.api.serializers import ActivitySerializer
from ...models import Activity
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

# change this all to one view
# add delete and put activity 
class ActivityView(APIView):
    def post(self, request : Request, format=None) -> Response:
        queryset = Activity.objects.all()
        name : str = request.data.get("name")
        description : str = request.data.get("description")
        num : int = len(queryset)

        activity = Activity(description=description, num=num, name=name)
        activity_serializer = ActivitySerializer(instance=activity)
        if activity_serializer.is_valid():
            activity_serializer.save()
            return Response(activity_serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request : Request, format=None) -> Response:
        data = JSONParser().parse(request)
        num : int = data['num']
        try:
            activity = Activity.objects.get(num=num)
            activity_serializer = ActivitySerializer(instance=activity, data=data)
            if activity_serializer.is_valid():
                activity_serializer.save()
                return Response(activity_serializer.data, status=status.HTTP_202_ACCEPTED)
        except Activity.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            

    def get(self, request : Request, format=None) -> Response:
        data = JSONParser().parse(request)
        num : int = data['int']
        try:
            activity = Activity.objects.get(num=num)
            activity_serializer = ActivitySerializer(activity)
            return Response(activity_serializer.data, status=status.HTTP_200_OK)
        except Activity.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request: Request, format=None) -> Response:
        data = JSONParser().parse(request)
        num : int = data['num']
        try:
            activity = Activity.objects.get(num=num)
            activity.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Activity.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
