from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import MovieSerializer,MovieScheduleSerializer,TheaterSerializer, HashTagSerializers, ReviewSerializer, AllReviewSerializer
from .models import Movie, Hashtag, ReviewReaction, Review
from accounts.models import UserLocation
from rest_framework.permissions import IsAuthenticated, AllowAny
from theater_managemant.models import Theater
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.http import JsonResponse
from theater_managemant.models import Theater
from django.contrib.gis.measure import D  
from screen_management.models import MovieSchedule,DailyShow
from django.db.models import Q 
from datetime import date
from rest_framework.permissions import IsAuthenticatedOrReadOnly 
from collections import defaultdict
from rest_framework.exceptions import NotFound
from geopy.distance import geodesic 





def get_nearby_theaters(lat,lng):
    user_location = Point(float(lng), float(lat), srid=4326)
    radius = 50000

    nearby_theaters = (
        Theater.objects
        .filter(is_approved=True, geom__distance_lte=(user_location, D(m=radius)), )
        .annotate(distance=Distance('geom', user_location))
        .order_by('distance')
    )

    return nearby_theaters

class AddMovieView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        tmdb_id = request.data.get('tmdb_id')
        try:
            movieobj = Movie.objects.get(tmdb_id = tmdb_id)
            if movieobj:
                return Response({"message": "Movie is already listed"},status=status.HTTP_409_CONFLICT)
        except Movie.DoesNotExist:
            pass

        serializer = MovieSerializer(data=request.data)
        
        if serializer.is_valid():
            movie = serializer.save()
            return Response({"message": "Movie created successfully", "movie_id": movie.id}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GetMovieView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):

        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)



    


class RemoveMovieView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        movie_id = request.data.get('id')
        if not movie_id:
            return Response({"message":"movie id not found"}, status=status.HTTP_204_NO_CONTENT)
        try:
            movie = Movie.objects.get(tmdb_id = movie_id)
            if movie:
                movie.delete()
        except Movie.DoesNotExist:
            return Response({"message":"movie does not exist in the db"}, status=status.HTTP_404_NOT_FOUND)
        

        return Response({"message":"movie deleted"},status=status.HTTP_200_OK)


class FullMovieDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request, movieId):
        movieId = Movie.objects.filter(tmdb_id = movieId).first()



class LocationMoviesView(APIView):
    permission_classes = []

    def post(self,request):
        now_showing_movies = MovieSchedule.objects.all(
        ).values('movie').distinct()
        distinct_movies = Movie.objects.filter(id__in=[item['movie'] for item in now_showing_movies])
        all_movies_data = MovieSerializer(distinct_movies, many=True).data
        lat = request.data.get("lat")
        lng = request.data.get("lng")
        address = request.data.get('address')
        if request.user.is_authenticated:
            try:
                user_location = UserLocation.objects.get(user=request.user)
                user_location.lat, user_location.lng, user_location.location = lat, lng, address
                user_location.save()
            except UserLocation.DoesNotExist:

                user_location = UserLocation.objects.create(user=request.user, lat=lat, lng=lng, location=address)
            
        if not lat or not lng:
            data = {
                "location":True,
                "upcoming":None,
                "now_showing":all_movies_data,
            }
            return Response({"error": "User location not found.","data":data},status=status.HTTP_404_NOT_FOUND)
        nearby_theaters = get_nearby_theaters(lat, lng)
        now_showing_movies = MovieSchedule.objects.filter(
        start_date__lte=date.today(),
        end_date__gte = date.today(),
        showtime__screen__theater__in=nearby_theaters
        ).values('movie').distinct()

        if not now_showing_movies or not nearby_theaters:
                data = {
                    "location":True,
                    "upcoming":None,
                    "now_showing":all_movies_data,
                }
                return Response({"error": "User location not found.","data":data},status=status.HTTP_404_NOT_FOUND)


        upcoming_movies = MovieSchedule.objects.filter(
        movie__release_date__gt=date.today(),
        showtime__screen__theater__in=nearby_theaters
        ).values('movie').distinct()
        print("upcoming movie before: ",upcoming_movies)

        distinct_now_showing_movies = Movie.objects.filter(id__in=[item['movie'] for item in now_showing_movies])
        distinct_upcoming_movies = Movie.objects.filter(id__in=[item['movie'] for item in upcoming_movies])

        now_showing_data = MovieSerializer(distinct_now_showing_movies, many=True).data
        upcoming_data = MovieSerializer(distinct_upcoming_movies, many=True).data


        data = {
            "upcoming":upcoming_data,
            "now_showing":now_showing_data,
        }
        print("this response:",now_showing_movies)


        return Response(data,status=status.HTTP_200_OK)
    



def calculate_distance(lat1, lng1, lat2, lng2):
    return geodesic((lat1, lng1), (lat2, lng2)).kilometers



from datetime import timedelta
from django.utils import timezone

class LocationTheatersView(APIView):
    permission_classes = []

    def post(self,request):
        lat = request.data.get("lat")
        lng = request.data.get("lng")

        if request.user.is_authenticated:
            user_location = UserLocation.objects.get(user=request.user)
            lat, lng = user_location.lat, user_location.lng

        nearby_theaters = get_nearby_theaters(lat, lng)
        if not nearby_theaters:
            return Response({"message": "This Movie is currently unavailable in this location"}, status=status.HTTP_404_NOT_FOUND)

        movie_id = request.data.get('id')
        movie = Movie.objects.get(id=movie_id)

        today = timezone.now().date()
        end_date = today + timedelta(days=5)

        schedules = MovieSchedule.objects.filter(
            movie_id=movie_id,
            start_date__lte=end_date,
            end_date__gte=today,
            showtime__screen__theater__in=nearby_theaters
        ).select_related("showtime__screen", "showtime__screen__theater")

        response_data = defaultdict(lambda: defaultdict(lambda: {"screens": defaultdict(list), "address": None, "distance_km": None}))
        theater_info = {} 
        for schedule in schedules:
            daily_shows = DailyShow.objects.filter(
                schedule=schedule,
                show_date__range=(today, end_date)
            )

            theater = schedule.showtime.screen.theater
            theater_name = theater.name
            theater_id = theater.id
            screen_name = schedule.showtime.screen.name
            screen_type = schedule.showtime.screen.type
            theater_location = (theater.lat, theater.lng)

            if theater_name not in theater_info:
                theater_distance = calculate_distance(lat, lng, theater_location[0], theater_location[1])
                theater_info[theater_name] = {
                    "address": theater.location,
                    "distance_km": round(theater_distance, 2),
                    "theater_id":theater_id
                }

            for show in daily_shows:
                date_str = str(show.show_date)
                response_data[date_str][theater_name]["screens"][screen_name].append([show.show_time.strftime("%H:%M"),screen_type])

                response_data[date_str][theater_name]["address"] = theater_info[theater_name]["address"]
                response_data[date_str][theater_name]["distance_km"] = theater_info[theater_name]["distance_km"]
                response_data[date_str][theater_name]["theater_id"] = theater_info[theater_name]["theater_id"]

        formatted_response = {
            date: {
                theater: {
                    "address": details["address"],
                    "distance_km": details["distance_km"],
                    "theater_id":details["theater_id"],
                    "screens": {
                        screen: times
                        for screen, times in details["screens"].items()
                    }
                }
                for theater, details in theaters.items()
            }
            for date, theaters in response_data.items()
        }

        return Response({'message': 'success response', "data": formatted_response}, status=status.HTTP_200_OK)
    

class MovieHashtagsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        hashtags = Hashtag.objects.all()
        serializer = HashTagSerializers(hashtags, many=True)
        
        return Response(data=serializer.data,status=status.HTTP_200_OK)
    

class MovieReviewView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        user = request.user
        try:
            review = Review.objects.get(user=user)

            if review:
                return Response({"message":"User is alrady rated this movie"}, status=status.HTTP_400_BAD_REQUEST)
        except Review.DoesNotExist:
            pass
        print(request.data)
        rating = request.data.get('rating')
        request.data['rating'] = float(rating)
        serializer = ReviewSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            review = serializer.save()
            return Response(
                {"message": "Review created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )

        error_messages = {field: error for field, error in serializer.errors.items()}

        return Response(
            {
                "message": "Failed to create review",
                "errors": error_messages
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    

    def get(self, request, movieId):
        try:
            movie = Movie.objects.get(id=movieId)
        except Movie.DoesNotExist:
            raise NotFound(f"Movie with id {movieId} not found.")
        reviews = Review.objects.filter(movie=movie).order_by('created_at','-likes_count', '-dislikes_count')
        
        serializer = AllReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND
from .models import Review, ReviewReaction

class ReviewReactionView(APIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users can react

    def post(self, request):
        user = request.user
        review_id = request.data.get('reviewId')
        reaction = request.data.get('reaction')
        
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({"error": "Review not found."}, status=HTTP_404_NOT_FOUND)
        
        opposite_reaction = 'dislike' if reaction == 'like' else 'like'

        review_reaction, created = ReviewReaction.objects.update_or_create(
            review=review, user=user,
            defaults={'reaction': reaction}
        )

        ReviewReaction.objects.filter(review=review, user=user, reaction=opposite_reaction).delete()

        like_count = ReviewReaction.objects.filter(review=review, reaction='like').count()
        dislike_count = ReviewReaction.objects.filter(review=review, reaction='dislike').count()
        review.likes_count = like_count
        review.dislikes_count = dislike_count
        review.save()

        return Response({
            "message": "Reaction updated successfully.",
            "likes": like_count,
            "dislikes": dislike_count,
            "currentReaction": reaction
        }, status=HTTP_200_OK)
