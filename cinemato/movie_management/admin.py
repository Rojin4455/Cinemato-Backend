from django.contrib import admin
from .models import Movie,Person,Genre,Language,MovieRole

admin.site.register(Movie)
admin.site.register(Person)
admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(MovieRole)

# Register your models here.
