
from django.urls import path
from .views import *



urlpatterns = [
    path('login/',AdminLogin.as_view(),name='login'),
    path('allusers/',AllUsers.as_view(),name='all-users')
]