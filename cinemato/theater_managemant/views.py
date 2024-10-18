from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
import rest_framework.status
from rest_framework.permissions import IsAuthenticated
from .serializers import TheaterSerializer,ScreenSerializer
from rest_framework import status
from .models import Theater,Screen,Tier,Seat,ScreenImage
import json
import cloudinary.uploader






class AddTheaterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        data = request.data.copy()
        data['owner'] = request.user.id


        image_file = request.FILES.get('photo')
        if image_file:
            upload_result = cloudinary.uploader.upload(
                image_file,
                folder="theater_photos"
            )
            image_url = upload_result.get('secure_url')
            data['image_url'] = image_url


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
    

class GetTheaterDetailsClass(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,theaterId):

        try:
            theater = Theater.objects.get(id = theaterId)
            screens= Screen.objects.filter(theater = theater)

            # screen_details = {}
            # tier_details = {}

            # for screen in screens:
            #      image = ScreenImage.objects.filter(screen=screen)
            #      tier = Tier.objects.filter(screen=screen)
            #      for i in tier:
            #         try:
            #             seats = Seat.objects.get(tier=i)
            #             tier_details[i.name] = seats
            #         except:
            #              tier_details[i.name] = None
            #      screen_details[screen.name] = {"images":image,"tier":tier_details}

            # print(f"screen: {screen_details}")
            theater_serializer = TheaterSerializer(theater, many=False)
            screen_serializer = ScreenSerializer(screens, many=True)

            return Response({"message":"theater details","data":theater_serializer.data,"screen_datas":screen_serializer.data},status=status.HTTP_200_OK)
        except Theater.DoesNotExist:
            return Response({"message":"theater is not found in that id {theaterId}"},status=status.HTTP_404_NOT_FOUND)
        

class AddScreenClass(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,theaterId):
        try:
                theater = Theater.objects.get(id=theaterId)
        except Theater.DoesNotExist:
                return Response({"error": "Theater not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Add theater to the incoming data
        tiers_data = json.loads(request.POST.get('tiers', '[]'))
        data = request.data.dict()
        # data = request.data.copy()
        # data.setlist('tiers', tiers_data)
        data['theater'] = theater.id

        if 'tiers' in data:
                try:
                    data['tiers'] = json.loads(data['tiers'])
       

                except json.JSONDecodeError:
                    return Response({"error": "Invalid JSON format for tiers"}, status=status.HTTP_400_BAD_REQUEST)
        print("request data after parsing before sending to serializer: ",data)
        # Create screen serializer and validate the data
        serializer = ScreenSerializer(data=data,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("serialiser data: ",serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ScreenDetailsClass(APIView):
     permission_classes = [IsAuthenticated]

     def get(self,request,screen_id):
        try:
            screen = Screen.objects.get(id = screen_id)
            theater_id = screen.theater.id
            serializer = ScreenSerializer(screen,many=False)
            print("reached", screen)
            return Response({"message":"screen details found successfully","data":serializer.data,"theater_id":theater_id}, status=status.HTTP_200_OK)
        except Exception as e:
             print(str(e))
             return Response({"message":"Screen not exist in this id"}, status=status.HTTP_404_NOT_FOUND)
