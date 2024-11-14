from rest_framework import serializers
from screen_management.models import ShowTime,SeatBooking,MovieSchedule,DailyShow


class SeatLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatBooking
        fields = "__all__"


