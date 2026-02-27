from django.contrib.gis.db import models
    
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
        return f"{self.name} ({self.get_source_display()})"
