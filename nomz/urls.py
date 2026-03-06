from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Restaurant Profile Management
    path('restaurant/profile/', views.restaurant_profile, name='restaurant_profile'),
    path('restaurant/create/', views.create_restaurant_profile, name='create_restaurant'),
    path('restaurant/edit/', views.edit_restaurant_profile, name='edit_restaurant'),
    path('restaurant/availability/', views.manage_availability, name='manage_availability'),
    path('restaurant/activate/', views.manage_activation, name='manage_activation'),
    
    # Restaurant Photo Management
    path('restaurant/photos/', views.restaurant_photos, name='restaurant_photos'),
    path('restaurant/photos/upload/', views.upload_photo, name='upload_photo'),
    path('restaurant/photos/<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),
    path('restaurant/photos/<int:photo_id>/set-primary/', views.set_primary_photo, name='set_primary_photo'),
]
