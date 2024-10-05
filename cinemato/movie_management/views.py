from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import MovieSerializer
from .models import Movie
from rest_framework.permissions import IsAuthenticated

class AddMovieView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        tmdb_id = request.data.get('tmdb_id')
        try:
            movieobj = Movie.objects.get(tmdb_id = tmdb_id)
            if movieobj:
                print("FF")
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


# class CheckMovieView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self,request,id):
#         try:
#             movieobj = Movie.objects.get(tmdb_id = id)
#             if movieobj:
#                 return Response({"message": "Movie is already listed"},status=status.HTTP_202_ACCEPTED)
#         except Movie.DoesNotExist:
#             return Response({"Message":"movie is not listed",},status=status.HTTP_200_OK)

    


class RemoveMovieView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        movie_id = request.data.get('id')
        print("movie id",movie_id)
        if not movie_id:
            return Response({"message":"movie id not found"}, status=status.HTTP_204_NO_CONTENT)
        try:
            movie = Movie.objects.get(tmdb_id = movie_id)
            if movie:
                movie.delete()
        except Movie.DoesNotExist:
            print("Object Does not Exit")
            return Response({"message":"movie does not exist in the db"}, status=status.HTTP_404_NOT_FOUND)
        
        print("movie id: ",movie_id)

        return Response({"message":"movie deleted"},status=status.HTTP_200_OK)


class FullMovieDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request, movieId):
        movieId = Movie.objects.filter(tmdb_id = movieId).first()

