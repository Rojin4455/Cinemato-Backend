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
    geom = gis_models.PointField(srid=4326, blank=True, null=True)  # Geospatial field
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.geom = Point(float(self.lng), float(self.lat), srid=4326)
        super(Theater, self).save(*args, **kwargs)

