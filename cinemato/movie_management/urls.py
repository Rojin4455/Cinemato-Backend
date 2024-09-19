from django.urls import path
from .views import *
print("here")
urlpatterns = [
    path('add-movie/', AddMovieView.as_view(), name='add-movie'),
    path('get-movie/', GetMovieView.as_view(), name='get-movie'),
]
