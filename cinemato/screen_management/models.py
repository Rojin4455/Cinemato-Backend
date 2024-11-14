from django.db import models
from theater_managemant.models import Screen,Seat,Tier
from accounts.models import User
from datetime import timedelta
from django.db import transaction
from movie_management.models import Movie

class ShowTime(models.Model):
    screen = models.ForeignKey(Screen, related_name='showtimes', on_delete=models.CASCADE)
    # movie = models.ForeignKey(Movie, related_name='showtimes', on_delete=models.CASCADE, null=True, blank=True)
    # start_time = models.DateTimeField(default=None)
    start_time = models.TimeField(default=None)
    # end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.screen.name} - {self.start_time}"


class MovieSchedule(models.Model):
    showtime = models.ForeignKey(ShowTime, related_name='schedules', on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, related_name='schedules', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.movie.title} at {self.showtime.screen.name} from {self.start_date} to {self.end_date}"
    

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            self.initialize_schedule()

    def initialize_schedule(self):

        with transaction.atomic():
            date = self.start_date
            while date <= self.end_date:
                daily_show = DailyShow.objects.create(
                    schedule=self,
                    show_date=date,
                    show_time=self.showtime.start_time
                )

                self._initialize_seat_bookings(daily_show)
                date += timedelta(days=1)

    def _initialize_seat_bookings(self, daily_show):
        seats = Seat.objects.filter(tier__screen=self.showtime.screen)
        seat_bookings = [
            SeatBooking(
                daily_show=daily_show,
                seat=seat,
                status='available',
                seat_row=seat.row,
                seat_column=seat.column,
                tier_row=seat.tier.rows,
                tier_column=seat.tier.columns,
                identifier=seat.identifier,
                position = seat.tier.position,
                tier_name=seat.tier.name,
                tier_price=seat.tier.price,
            )
            for seat in seats
        ]
        SeatBooking.objects.bulk_create(seat_bookings)



class DailyShow(models.Model):
    schedule = models.ForeignKey(MovieSchedule, related_name='daily_shows', on_delete=models.CASCADE)
    show_date = models.DateField()
    show_time = models.TimeField()

    class Meta:
        unique_together = ('schedule', 'show_date', 'show_time')

    def __str__(self):
        return f"{self.schedule.movie.title} on {self.show_date} at {self.show_time}"
    



class SeatBooking(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('reserved', 'Reserved'),
        ('available', 'Available'),
    ]
    daily_show      = models.ForeignKey(DailyShow, related_name='seat_bookings', on_delete=models.CASCADE)
    user            = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    seat            = models.ForeignKey(Seat, related_name='bookings', null=True, blank=True, on_delete=models.SET_NULL)
    status          = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available',)
    reserved_at     = models.DateTimeField(null=True, blank=True)
    seat_row        = models.CharField(max_length=5)
    seat_column     = models.PositiveIntegerField()
    tier_row        = models.IntegerField()
    tier_column     = models.IntegerField()
    identifier      = models.CharField(max_length=5, null=True, blank=True)
    tier_name       = models.CharField(max_length=50)
    tier_price      = models.DecimalField(max_digits=5, decimal_places=2)
    position        = models.IntegerField(default=0)

    class Meta:
        unique_together = ('daily_show', 'seat')

    def reset_seat(self):
        self.status = 'available'
        self.user = None
        self.save()

    def __str__(self):
        return f"Seat {self.identifier} ({self.seat_row}-{self.seat_column}) for {self.daily_show.schedule.movie.title} on {self.daily_show.show_date} at {self.daily_show.show_time} in {self.daily_show.schedule.showtime.screen}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.seat_row = self.seat.row
            self.seat_column = self.seat.column
            self.tier_row = self.seat.tier.rows
            self.tier_column = self.seat.tier.columns
            self.identifier = self.seat.identifier
            self.tier_name = self.seat.tier.name
            self.tier_price = self.seat.tier.price
            self.position = self.seat.tier.position
        super().save(*args, **kwargs)


# class ShowDate(models.Model):
#     date = models.DateField()
#     screen = models.ForeignKey(Screen, related_name='showdate', on_delete=models.CASCADE)

# class BookingLayout:
#     STATUS_CHOICES = [
#         ('booked', 'Booked'),
#         ('reserved', 'Reserved'),
#         ('available', 'Available'),
#     ]
#     screen = models.ForeignKey(Screen, related_name="booking_layout", on_delete=models.CASCADE)
#     tier = models.ForeignKey(Tier, related_name='seats', on_delete=models.CASCADE)
#     row = models.CharField(max_length=5)
#     column = models.PositiveIntegerField()
#     is_available = models.BooleanField(default=False)
#     identifier = models.CharField(max_length=5, null=True, blank=True)
#     status = models.CharField(
#         max_length=10,
#         choices=STATUS_CHOICES,
#         default='available',
#     )
#     date = models.ForeignKey(ShowDate, related_name='booking_layout', on_delete=models.CASCADE)
#     time = models.ForeignKey(ShowTime, related_name='booking_layout', on_delete=models.CASCADE)

#     def __str__(self):
#         return f"Seat {self.tier.screen.name} - {self.tier.name} - {self.identifier} - {self.row} - {self.column}"
    







    # class Meta:
    #     unique_together = ('screen', 'start_time')


# class SeatBooking(models.Model):
#     show_time = models.ForeignKey(ShowTime, related_name='seat_bookings', on_delete=models.CASCADE)
#     seat = models.ForeignKey(Seat, related_name='bookings', on_delete=models.CASCADE)
#     user = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE)
#     is_booked = models.BooleanField(default=False)
#     booking_time = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Booking for {self.seat.identifier} at {self.show_time} by {self.user.email}"
    


# class MovieScheduleSample(models.Model):
#     movie_title = models.CharField(max_length=255)
#     time = models.TimeField()