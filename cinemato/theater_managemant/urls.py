from django.urls import path
from .views import *

urlpatterns = [
    path('add-theater/',AddTheaterView.as_view(),name='add-theater'),
    path('get-theaters/',GetTheaterView.as_view(),name='get-theater')
]
