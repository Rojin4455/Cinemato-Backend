from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import MovieSerializer
from .models import Movie
from rest_framework.permissions import IsAuthenticated

class AddMovieView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
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
    

