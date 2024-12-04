from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
import rest_framework.status
from rest_framework.permissions import IsAuthenticated
from .serializers import TheaterSerializer,ScreenSerializer,SnackCategorySerializer, SnackItemSerializer, TheaterSnackSerializer, TheaterFullSnacksSerializer
from rest_framework import status
from .models import Theater,Screen,Tier,Seat,ScreenImage,SnackCategory,SnackItem,TheaterSnack
import json
import cloudinary.uploader
from django.db.models import Prefetch
from accounts.models import User







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
        theater = Theater.objects.filter(owner=request.user)
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

            print("after here reached",screen_id)
            screen = Screen.objects.get(id = screen_id)
            screen = Screen.objects.prefetch_related(
            Prefetch('tiers', queryset=Tier.objects.order_by('id'))).get(id=screen_id)
            theater_id = screen.theater.id
            serializer = ScreenSerializer(screen,many=False)
            print("reached", screen)
            return Response({"message":"screen details found successfully","data":serializer.data,"theater_id":theater_id}, status=status.HTTP_200_OK)
        except Exception as e:
             print(str(e))
             return Response({"message":"Screen not exist in this id"}, status=status.HTTP_404_NOT_FOUND)
        



class SnackCategoryClass(APIView):
    permission_classes = [IsAuthenticated]


    def post(self,request):
        category_name = request.data.get('category_name')
        try:
            owner = User.objects.get(id=request.user.id)
            try:
                SnackCategory.objects.get(name=category_name, owner=owner)
                return Response({"message":"Category is Already exists"}, status=status.HTTP_400_BAD_REQUEST)
            except SnackCategory.DoesNotExist:
                new_category = SnackCategory.objects.create(name=category_name, owner=owner)
                serializer = SnackCategorySerializer(new_category)
                print("serializers", serializer.data)
                return Response({"message":"category created successfully","data":serializer.data}, status=status.HTTP_201_CREATED)
                    
            
                    
        except User.DoesNotExist:
            return Response({"message":"Owner is not Found"}, status=status.HTTP_404_NOT_FOUND)
        
    def get(self, request):
        all_categories = SnackCategory.objects.all()
        
        serializer = SnackCategorySerializer(all_categories, many=True)
        return Response({"message":"All categories fetched successfully", "data":serializer.data}, status=status.HTTP_200_OK)
    


class OwnerSnacksClass(APIView):
    def post(self, request):
        snack_data = request.data
        print("snack data: ", snack_data)

        try:
            category = SnackCategory.objects.get(name=snack_data['category'], owner=request.user)
        except SnackCategory.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        snack_data = snack_data.copy()
        snack_data['category'] = category.id
        snack_data['is_vegetarian'] = False if snack_data.pop('is_vegetarian') == ["false"] else True

        serializer = SnackItemSerializer(data=snack_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        


class TheaterSnacksClass(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        print("request data:",request.data)
        serializer = TheaterSnackSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self,request,theater_id):
        print("theater id: ",theater_id)
        theater = Theater.objects.get(id=theater_id)
        existing_snacks = TheaterSnack.objects.filter(theater=theater)
        available_snacks = SnackItem.objects.exclude(theater_snack_items__in=existing_snacks)
        available_categories = SnackCategory.objects.filter(snack_items__in=available_snacks).distinct()
        print("available snacks: ",available_snacks)
        serializer = SnackCategorySerializer(available_categories, many=True, context={'snacks': available_snacks})

        return Response({"message":"All categories fetched successfully in theater snacks", "data":serializer.data}, status=status.HTTP_200_OK)
    
class AddedSnacksClass(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,theater_id):
        theater = Theater.objects.get(id=theater_id)
        existing_snacks = TheaterSnack.objects.filter(theater=theater)
        serializer = TheaterFullSnacksSerializer(existing_snacks, many=True)
        # added_snacks = SnackItem.objects.filter(theater_snack_items__in=existing_snacks)
        # available_categories = SnackCategory.objects.filter(snack_items__in=added_snacks).distinct()
        # serializer = SnackCategorySerializer(available_categories, many=True, context={'snacks': added_snacks})

        return Response({"message":"All categories fetched successfully in theater added snacks", "data":serializer.data}, status=status.HTTP_200_OK)
    

class UpdateSnackTheater(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        snack_id = request.data.get('snack_id')
        new_stock = request.data.get('stock')
        price = request.data.get('price')

        try:
            snack = TheaterSnack.objects.get(id=snack_id)
            snack.stock = new_stock if new_stock else snack.stock
            snack.price = price if price else snack.price
            snack.save()
            return Response(status=status.HTTP_200_OK)

        except TheaterSnack.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


    def delete(self,request,snack_id):
        print("snack id: ",snack_id)
        if snack_id:
            try:
                snack = TheaterSnack.objects.get(id=snack_id)
                snack.delete()
                print("snack is deleted")
                return Response(status=status.HTTP_200_OK)
            except TheaterSnack.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({'message':"invalid details provided"}, status=status.HTTP_400_BAD_REQUEST)





        


        


