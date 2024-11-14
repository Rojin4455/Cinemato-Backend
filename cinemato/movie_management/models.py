from django.db import models

class Genre(models.Model):
    tmdb_id = models.IntegerField()
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Person(models.Model):
    name = models.CharField(max_length=255)
    image = models.URLField(max_length=200, blank=True, null=True) 
    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255)
    tmdb_id = models.IntegerField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    vote_average = models.FloatField(blank=True, default=0)
    runtime = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, default="No description available.")
    poster_path = models.URLField(max_length=500, blank=True, null=True)  # URL for poster image
    backdrop_path = models.URLField(max_length=500, blank=True, null=True)  # URL for backdrop image
    video_key = models.CharField(max_length=225, blank=True, null=True)
    is_listed = models.BooleanField(default=True)

    # Relationships
    genres = models.ManyToManyField(Genre, related_name='movies')  # Many-to-many relation with genres
    languages = models.ManyToManyField(Language, related_name='movies')  # Many-to-many relation with languages

    def __str__(self):
        return self.title
    


class MovieRole(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='roles') 
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='roles')  
    role = models.CharField(max_length=50, blank=True, null=True)
    character_name = models.CharField(max_length=255, blank=True, null=True)
    is_cast = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.person.name} - {self.role} in {self.movie.title}"


