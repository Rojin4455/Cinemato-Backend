from django.urls import path
from .views import *

urlpatterns = [
    path('seat-layout/',SeatLayoutClass.as_view(), name="seat-layout"),
    path('add-selected-seats/', SeleacedSeatsClass.as_view()),
    path('get-added-snack/<int:theater_id>/',AddedSnacksClass.as_view())
]