from django.db import models
from django.contrib.gis.geos import Point
from django.contrib.gis.db import models as gis_models
from accounts.models import User

class Theater(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    lat = models.DecimalField(max_digits=25, decimal_places=20)
    lng = models.DecimalField(max_digits=25, decimal_places=20)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    total_screens = models.IntegerField()
    screen_types = models.JSONField()
    is_food_and_beverages = models.BooleanField(default=False)
    is_parking = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='theater_photos/', blank=True, null=True)
    image_url = models.URLField(max_length=500, default="")
    geom = gis_models.PointField(srid=4326, blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.geom = Point(float(self.lng), float(self.lat), srid=4326)
        super(Theater, self).save(*args, **kwargs)



class Screen(models.Model):
    theater = models.ForeignKey(Theater, related_name='screens', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(null=True,default=0)

    def __str__(self):
        return f"{self.name} - {self.theater.name}"
    
class ScreenImage(models.Model):
    screen = models.ForeignKey(Screen, related_name='screen_images', on_delete=models.CASCADE)
    # image = models.ImageField(upload_to='screen_photos/', blank=True, null=True)
    image_url = models.URLField(max_length=500)

    def __str__(self):
        return f"{self.screen} - {self.image_url}"

    

class Tier(models.Model):
    screen = models.ForeignKey(Screen, related_name='tiers', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    total_seats = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.screen.name}"
    
    def save(self, *args, **kwargs):
        if self.pk:
            previous_tier = Tier.objects.get(pk=self.pk)
            seat_difference = self.total_seats - previous_tier.total_seats
            self.screen.capacity += seat_difference
        else:
            self.screen.capacity += self.total_seats
        

        self.screen.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.screen.capacity -= self.total_seats
        self.screen.save()
        super().delete(*args, **kwargs) 

    

class Seat(models.Model):
    tier = models.ForeignKey(Tier, related_name='seats', on_delete=models.CASCADE)
    # row = models.CharField(max_length=5)
    # column = models.PositiveIntegerField()
    # is_available = models.BooleanField(default=False)
    seat_layout = models.JSONField()

    def __str__(self):
        seat_info = self.seat_layout.get("identifier", "Unknown")
        return f"Seat {seat_info} - {self.tier.name} - {self.tier.screen.name}"
    

