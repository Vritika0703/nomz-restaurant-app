from django.urls import path
from . import api_views, views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('home/', views.home, name='home'),
    path('map/', views.map_view, name='map'),
    path('api/restaurants/map-data/', api_views.map_restaurant_data, name='api_restaurants_map'),
    path('register/', views.register, name='register'), # Removed <str:role>
    path('login/', views.user_login, name='login'),     # Removed <str:role>
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
