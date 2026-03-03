from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    # The available roles
    ROLE_CHOICES = [
        ('diner', 'Diner'),
        ('restaurant', 'Restaurant'),
    ]
    
    # Links this profile to the built-in Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='diner')

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    neighborhood = models.CharField(max_length=100)
    description = models.TextField()
    cuisine = models.CharField(max_length=100)
    # We use a simple CharField for neighborhood to keep it easy for now
    
    def __str__(self):
        return self.name
"""from django.contrib.gis.db import models
    
class Restaurant(models.Model):
    # Data source tracking
    SOURCE_CHOICES = [
        ('EATERIES', 'Directory of Eateries'),
        ('DINING_OUT', 'Dining Out NYC'),
    ]
    
    name = models.CharField(max_length=255)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    external_id = models.CharField(max_length=100, unique=True, null=True)
    
    # Coordinates for the map (Point contains Longitude and Latitude)
    location = models.PointField(srid=4326) 
    
    # Metrics for your "Composite Score"
    cuisine_type = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_source_display()})" """
