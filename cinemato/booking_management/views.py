from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from theater_managemant.models import Theater, Screen
from screen_management.models import ShowTime,MovieSchedule,DailyShow,SeatBooking
from .serializers import SeatLayoutSerializer
from collections import defaultdict
from theater_managemant.models import TheaterSnack
from theater_managemant.serializers import TheaterFullSnacksSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone



def month_converter(month):
    monthMap = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5,"Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10,"Nov": 11, "Dec": 12}

    return monthMap[month]

class SeatLayoutClass(APIView):
    permission_classes = []

    def post(self, request):
        # Get required parameters
        theater_id = request.data.get('theater_id')
        screen_name = request.data.get('screen_name')
        screen_time = request.data.get('screen_time')
        show_date = request.data.get('date')

        # Validate input
        if not all([theater_id, screen_name, screen_time, show_date]):
            return Response(
                {"error": "Missing required fields: theater_id, screen_name, screen_time, date"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            theater = Theater.objects.get(id=theater_id)
            
            screen = Screen.objects.get(theater=theater, name__iexact=screen_name)
            
            time = ShowTime.objects.get(screen=screen, start_time=screen_time)

            movie_schedule = MovieSchedule.objects.get(showtime=time)

            daily_show = DailyShow.objects.get(schedule=movie_schedule, show_date=show_date)

            seats = SeatBooking.objects.filter(daily_show=daily_show).order_by('position', 'identifier')
            
            grouped_seats = defaultdict(list)
            for seat in seats:
                data = SeatLayoutSerializer(seat).data
                grouped_seats[seat.position].append(data)

        except Theater.DoesNotExist:
            return Response(
                {"error": f"Theater with id {theater_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Screen.DoesNotExist:
            return Response(
                {"error": f"Screen '{screen_name}' not found in theater with id {theater_id}."},
                status=status.HTTP_404_NOT_FOUND
            )
        except ShowTime.DoesNotExist:
            return Response(
                {"error": f"ShowTime with start time '{screen_time}' not found for screen '{screen_name}'."},
                status=status.HTTP_404_NOT_FOUND
            )
        except MovieSchedule.DoesNotExist:
            return Response(
                {"error": "Movie schedule not found for the specified showtime."},
                status=status.HTTP_404_NOT_FOUND
            )
        except DailyShow.DoesNotExist:
            return Response(
                {"error": f"No daily show found on date '{show_date}' for the specified schedule."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(data=grouped_seats, status=status.HTTP_200_OK)
    


class SeleacedSeatsClass(APIView):
    permission_classes = []

    def post(self,request):
        selected_theater = request.data.get("selected_theater")
        selected_seats = request.data.get("selected_seats")
        selected_date = request.data.get("selected_date")
        selected_time = request.data.get("selected_time")
        screen_name = request.data.get("screen_name")
        tier_name = request.data.get("tier")
        
        # print("selected theater : ",selected_theater)
        # print("selected selected_seats : ",selected_seats)
        # print("selected selected_date : ",selected_date)
        # print("selected selected_time : ",selected_time)
        # print("selected screen : ",screen_name)

        
        daily_show = get_object_or_404(DailyShow, schedule__showtime__screen__name = screen_name, show_date=str(selected_date['year']) + '-' + str(month_converter(selected_date['month'])) + '-' + str(selected_date['day']), show_time = selected_time)
        identifiers = []
        for seat in selected_seats:
            identifiers.append(seat['identifier'])

        if daily_show:
            seats = SeatBooking.objects.filter(daily_show = daily_show, identifier__in = identifiers)

            for seat in seats:
                if seat.status == 'available':
                    seat.status = 'reserved'
                    seat.reserved_at = timezone.now()
                else:
                    seat.status = 'available'
                    seat.reserved_at = None
                seat.save()

        
        return Response(status=status.HTTP_200_OK)



class AddedSnacksClass(APIView):
    permission_classes = []

    def get(self,request,theater_id):
        theater = Theater.objects.get(id=theater_id)
        existing_snacks = TheaterSnack.objects.filter(theater=theater)
        serializer = TheaterFullSnacksSerializer(existing_snacks, many=True)
        # added_snacks = SnackItem.objects.filter(theater_snack_items__in=existing_snacks)
        # available_categories = SnackCategory.objects.filter(snack_items__in=added_snacks).distinct()
        # serializer = SnackCategorySerializer(available_categories, many=True, context={'snacks': added_snacks})

        return Response({"message":"All categories fetched successfully in theater added snacks", "data":serializer.data}, status=status.HTTP_200_OK)