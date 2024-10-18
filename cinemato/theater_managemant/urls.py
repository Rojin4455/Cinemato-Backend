from django.urls import path
from .views import *

urlpatterns = [
    path('add-theater/',AddTheaterView.as_view(),name='add-theater'),
    path('get-theaters/',GetTheaterView.as_view(),name='get-theaters'),
    path("theater-details/<int:theaterId>/", GetTheaterDetailsClass.as_view(), name="theater-details"),
    path("add-screen/<int:theaterId>/",AddScreenClass.as_view(),name="add-theater"),
    path('screen-details/<int:screen_id>/',ScreenDetailsClass.as_view(), name='screen-details'),

]
