from ...models import Activity
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

class CreateActivityView(APIView):
    def post(self, request, format=None):
        queryset = Activity.objects.all()
        name = request.data.get("name")
        description = request.data.get("description")
        num = len(queryset)
        activity = Activity(description=description, num=num, name=name)
        activity.save()
        return Response({'success':True}, status=status.HTTP_201_CREATED)

class GetActivityView(APIView):
    def post(self, request, format=None):
        num = request.data.get("num")
        queryset = Activity.objects.filter(num=num)
        if queryset:
            activity = queryset[0]
            return Response({"name" : activity.name, "description" : activity.description}, status=status.HTTP_200_OK)
        else:
            return Response({"Status" : "Not Found"}, status=status.HTTP_404_NOT_FOUND)