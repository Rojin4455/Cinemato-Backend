from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from theater_managemant.models import Tier,Screen, Seat
from rest_framework.response import Response
from rest_framework import status
from .serializers import SeatLayoutSerializer,ShowTimesSerializer,MovieScheduleSerializer
from theater_managemant.views import ScreenDetailsClass
from django.urls import reverse
from django.http import HttpResponseRedirect
import datetime
import pytz
from dateutil import parser
from .models import ShowTime,MovieSchedule,DailyShow
from movie_management.serializers import MovieSerializer
from datetime import date as date_method





class AddTierLayoutClass(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):

        tier_id = request.data.get('payload')['tierFullDetails']['id']
        tier = Tier.objects.get(id=tier_id)
        screen_id = tier.screen.id
        request.data["tier_id"] = tier_id
        serializer = SeatLayoutSerializer(data=request.data.get('payload'), context={'tier_id': tier_id})
        if serializer.is_valid():
            serializer.save()
            screen_details_view = ScreenDetailsClass()  # Create an instance of ScreenDetailsClass
            # Call the 'get' method of ScreenDetailsClass to fetch updated screen details
            response = screen_details_view.get(request, screen_id=screen_id)
            print("here is the response: ",response)
            print("here is the response screen id: ",screen_id)
            screen_details_url = reverse('screen-details', kwargs={'screen_id': screen_id})
                        # Perform the redirect to the ScreenDetailsClass view
            return HttpResponseRedirect(screen_details_url)
            # return Response({"message": "Seat layout saved successfully!"}, status=status.HTTP_201_CREATED)
            return response
        else:
            print("error:   ",serializer.errors)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EditSeatCountView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, tier_id):
        try:
            tier = Tier.objects.get(id=tier_id)
        except Tier.DoesNotExist:
            return Response({"error": "Tier not found"}, status=status.HTTP_404_NOT_FOUND)

        new_seat_count = request.data.get('total_seats', None)
        if new_seat_count is not None:
            tier.total_seats = int(new_seat_count)
            tier.save()
            return Response({"message": "Seat count updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid seat count"}, status=status.HTTP_400_BAD_REQUEST)
        

class ScreenTimeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        screen_time_data = request.data.get('time')
        screen_id = request.data.get('screen_id')
        screen = Screen.objects.get(id=screen_id)
        tiers = Tier.objects.filter(screen=screen)
        for tier in tiers:
            if not Seat.objects.filter(tier=tier):
                return Response({"message":"Seat Layout is not Completed"}, status=status.HTTP_400_BAD_REQUEST)
        # screen_time = parser.parse(screen_time_data)

        # local_tz = pytz.timezone('Asia/Kolkata')
        # screen_time_local = screen_time.astimezone(local_tz)      
        # time_only = screen_time_local.time()


        ShowTime.objects.create(screen=screen, start_time=screen_time_data)
        
        return Response({"message": "Show Time added successfully", "time": str(screen_time_data)}, status=status.HTTP_200_OK)
    

    def get(self,request,screen_id):

        screen = Screen.objects.get(id=screen_id)

        show_times = ShowTime.objects.filter(screen=screen)

        showtime_data = {}
        for index,showtime in enumerate(show_times):
            try:
                movie_schedule = MovieSchedule.objects.get(showtime=showtime)
                movie_data = MovieSerializer(movie_schedule.movie).data
            except MovieSchedule.DoesNotExist:
                movie_data = "None"

            showtime_data[index] = {
                "time": ShowTimesSerializer(showtime).data,  # Standard 12-hour format with AM/PM
                "movie": movie_data
            }
        # data = ShowTimesSerializer(show_times, many=True)
        
        # data = {
        #     "show_times":data.data
        # }

        response_data = {
            "message": "Show Times fetched successfully",
            "data": showtime_data
        }
        return Response(response_data,status=status.HTTP_200_OK)
    

    def delete(self,request):
        screen_time_data = request.data.get('time')
        screen_id = request.data.get('screen_id')
        screen = Screen.objects.get(id=screen_id)
        print(screen_time_data)
        # screen_time = parser.parse(screen_time_data)

        # local_tz = pytz.timezone('Asia/Kolkata')
        # screen_time_local = screen_time.astimezone(local_tz)      
        # time_only = screen_time_local.time()


        showtime = ShowTime.objects.get(start_time = screen_time_data, screen=screen)
        try:
            MovieSchedule.objects.get(showtime=showtime)
            return Response({"message":"A Movie Is currently running in this show time"}, status=status.HTTP_409_CONFLICT)
        except MovieSchedule.DoesNotExist:
            showtime.delete()

        return Response({"message": "Show Time deleted successfully", "time": str(screen_time_data)}, status=status.HTTP_200_OK)
    



class MovieScheduleView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        serializer = MovieScheduleSerializer(data=request.data)        
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Movie schedule created successfully"}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ShowDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,screen_id):
        screen = Screen.objects.get(id=screen_id)
        show_times = ShowTime.objects.filter(screen=screen)
        schedules = []
        for showtime in show_times:
            try:
                movie_schedule = MovieSchedule.objects.get(showtime=showtime)
                schedules.append(movie_schedule)
            except:
                pass

        if not schedules:
            return Response({"message":"no movies are currently running"},status=status.HTTP_404_NOT_FOUND)
        start_dates = end_dates = []
        for i in schedules:
            start_dates.append(i.start_date)
            end_dates.append(i.end_date)
        #     print(f"movie : {i.movie} --> start date: {i.start_date} --> end date: {i.end_date}" )

        # print(sorted(start_dates)[0])
        # print(sorted(end_dates)[-1])

        
        return Response({"message":"running shows times found successfully","data":{"startDate":sorted(start_dates)[0],"endDate":sorted(end_dates)[-1]}},status.HTTP_200_OK)
    

class DatedShowsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,screen_id,date):
        screen = Screen.objects.get(id=screen_id)

        show_times = ShowTime.objects.filter(screen=screen)
        showtime_data = {}
        date_parts = date.split("-")
        year = int(date_parts[0])
        day = int(date_parts[1])
        month = int(date_parts[2])

    
        show_date = date_method(year,month,day)
        for index,showtime in enumerate(show_times):
            try:

                movie_schedule = MovieSchedule.objects.get(showtime=showtime,daily_shows__show_date = show_date)

                movie_data = MovieSerializer(movie_schedule.movie).data
                showtime_data[index] = {
                "time": ShowTimesSerializer(showtime).data,
                "movie": movie_data
            }
            except Exception as e:
                movie_data = "None"

        
        response_data = {
            "message": "Show Times fetched successfully",
            "data": showtime_data
        }
        return Response(response_data,status=status.HTTP_200_OK)



        


# class ShowScreenDetailsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self,request,screen_id,date,time):
#         print("screen id: ",screen_id, "date: ",date, "time: ",time)
#         date_parts = date.split("-")
#         year = int(date_parts[0])
#         day = int(date_parts[1])
#         month = int(date_parts[2])
#         show_date = date_method(year,month,day)

#         daily_show = DailyShow.objects.filter(show_date = show_date, show_time = )

#         return Response(status=status.HTTP_200_OK)




class SetTimeView(APIView):
    def post(self, request):
        serializer = MovieScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the validated data to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)