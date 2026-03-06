from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


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
    """
    Restaurant profile model for restaurant owners to manage their business information.
    """
    CUISINE_CHOICES = [
        ('american', 'American'),
        ('asian', 'Asian'),
        ('italian', 'Italian'),
        ('mexican', 'Mexican'),
        ('indian', 'Indian'),
        ('french', 'French'),
        ('japanese', 'Japanese'),
        ('chinese', 'Chinese'),
        ('thai', 'Thai'),
        ('mediterranean', 'Mediterranean'),
        ('fusion', 'Fusion'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('other', 'Other'),
    ]

    PRICE_CHOICES = [
        ('$', 'Budget-Friendly ($)'),
        ('$$', 'Moderate ($$)'),
        ('$$$', 'Upscale ($$$)'),
        ('$$$$', 'Fine Dining ($$$$)'),
    ]

    # Owner and basic info
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant_profile')
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True, help_text='Describe your restaurant, cuisine style, and ambiance')
    
    # Location and contact
    address = models.CharField(max_length=500, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Restaurant details
    cuisine_type = models.CharField(max_length=50, choices=CUISINE_CHOICES, default='other')
    price_range = models.CharField(max_length=10, choices=PRICE_CHOICES, default='$$')
    
    # Operating hours
    days_of_week = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
    
    # Hours stored as JSONField for flexibility (optional: can use TimeField pairs)
    hours_open = models.TimeField(default='09:00', help_text='Opening time')
    hours_close = models.TimeField(default='21:00', help_text='Closing time')
    
    # Status and availability
    is_active = models.BooleanField(default=True, help_text='Profile is visible to customers')
    is_temporarily_unavailable = models.BooleanField(default=False, help_text='Temporarily mark as unavailable')
    unavailable_reason = models.CharField(max_length=500, blank=True, null=True)
    unavailable_until = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional: Coordinates for map (if using GeoDjango)
    # location = models.PointField(srid=4326, blank=True, null=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def is_open_now(self):
        """Check if restaurant is currently open"""
        if not self.is_active or self.is_temporarily_unavailable:
            return False
        
        current_time = timezone.now().time()
        return self.hours_open <= current_time <= self.hours_close
    
    def can_be_managed_by(self, user):
        """Check if a user can manage this restaurant"""
        return self.owner == user


class RestaurantPhoto(models.Model):
    """
    Model to handle multiple photos for a restaurant.
    """
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='restaurant_photos/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False, help_text='Set as main photo for the restaurant')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', '-uploaded_at']
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.caption or 'Photo'}"
    
    def save(self, *args, **kwargs):
        """Ensure only one primary photo"""
        if self.is_primary:
            # Remove primary status from other photos
            RestaurantPhoto.objects.filter(restaurant=self.restaurant, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
