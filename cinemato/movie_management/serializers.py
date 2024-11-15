from rest_framework import serializers
from .models import Genre, Language, Person, Movie, MovieRole
from screen_management.models import MovieSchedule,ShowTime, DailyShow
from theater_managemant.models import Theater,Screen

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['tmdb_id', 'name']

    def to_internal_value(self, data):
        
        try:
            genre = Genre.objects.get(tmdb_id=data.get('tmdb_id'))
        except Genre.DoesNotExist:
            genre = None

        if genre is not None:
            return genre
        
        
        return super().to_internal_value(data)



        return genre

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['name']

    def to_internal_value(self, data):
        
        try:
            language = Language.objects.get(name=data.get('name'))
        except Language.DoesNotExist:
            language = None

        if language is not None:
            return language
        return super().to_internal_value(data)

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['name', 'image']

class MovieRoleSerializer(serializers.ModelSerializer):
    person = PersonSerializer()

    class Meta:
        model = MovieRole
        fields = ['person', 'role', 'character_name', 'is_cast']

class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True)
    languages = LanguageSerializer(many=True)
    roles = MovieRoleSerializer(many=True)

    class Meta:
        model = Movie
        fields = [
            'title', 'tmdb_id', 'release_date', 'vote_average', 'runtime', 
            'description', 'poster_path', 'backdrop_path', 'video_key', 
            'is_listed', 'genres', 'languages', 'roles','id',   
        ]

    def create(self, validated_data):
        genres_data = validated_data.pop('genres')
        languages_data = validated_data.pop('languages')
        roles_data = validated_data.pop('roles')
        # Create or update the movie
        movie = Movie.objects.create(**validated_data)

        # Add genres
        for genre_data in genres_data:
            if isinstance(genre_data, Genre):
                genre = genre_data
            else:
                genre, created = Genre.objects.get_or_create(**genre_data)
            movie.genres.add(genre)

        # Add languages
        for language_data in languages_data:
            if isinstance(language_data, Language):
                language = language_data
            else:
                language, created = Language.objects.get_or_create(**language_data)
            movie.languages.add(language)

        # Add roles and persons
        for role_data in roles_data:
            person_data = role_data.pop('person')
            person, created = Person.objects.get_or_create(**person_data)
            movie_role_obj = MovieRole.objects.create(person=person, movie=movie, **role_data)
            movie_role_obj.is_cast = True if role_data['character_name'] else False
            movie_role_obj.save()
            


        return movie
    




class MovieScheduleSerializer(serializers.ModelSerializer):
    movie = MovieSerializer()
    class Meta:
        model = MovieSchedule
        fields = '__all__'









# class ShowTimeSerializer(serializers.ModelSerializer):
#     show_time = serializers.TimeField(source='start_time')

#     class Meta:
#         model = ShowTime
#         fields = ['show_time']

# class ScreenSerializer(serializers.ModelSerializer):
#     showtimes = ShowTimeSerializer(many=True, read_only=True)

#     class Meta:
#         model = Screen
#         fields = ['name', 'type', 'capacity', 'showtimes']

# class TheaterSerializer(serializers.ModelSerializer):
#     screens = ScreenSerializer(many=True, read_only=True)

#     class Meta:
#         model = Theater
#         fields = ['name', 'location', 'lat', 'lng', 'screens']

# class TheaterMovieScheduleSerializer(serializers.ModelSerializer):
#     theater = serializers.SerializerMethodField()

#     def get_theater(self, obj):
#         print("obj:",obj)

#         nearby_theaters = Theater.objects.filter(screens__showtimes__schedules=obj)
#         return TheaterSerializer(nearby_theaters, many=True).data

#     class Meta:
#         model = MovieSchedule
#         fields = ['theater', 'start_date', 'end_date']




from rest_framework import serializers


class DailyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyShow
        fields = ['show_date', 'show_time']

class ShowTimeSerializer(serializers.ModelSerializer):
    daily_shows = DailyShowSerializer(many=True, read_only=True)

    class Meta:
        model = ShowTime
        fields = ['id', 'start_time', 'daily_shows']

class ScreenSerializer(serializers.ModelSerializer):
    showtimes = ShowTimeSerializer(many=True, read_only=True)

    class Meta:
        model = Screen
        fields = ['id', 'name', 'type', 'capacity', 'showtimes']

class TheaterSerializer(serializers.ModelSerializer):
    screens = ScreenSerializer(many=True, read_only=True)

    class Meta:
        model = Theater
        fields = ['id', 'name', 'location', 'screens']



        
