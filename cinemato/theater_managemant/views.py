from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
import rest_framework.status
from rest_framework.permissions import IsAuthenticated
from .serializers import TheaterSerializer
from rest_framework import status
from .models import Theater




class AddTheaterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        data = request.data.copy()
        data['owner'] = request.user.id
        serializer = TheaterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetTheaterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        theater = Theater.objects.all()
        serializer = TheaterSerializer(theater,many=True)

        return Response(serializer.data)
