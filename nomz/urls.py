from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'), # Removed <str:role>
    path('login/', views.user_login, name='login'),     # Removed <str:role>
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search/', views.restaurant_search, name='restaurant_search'),
]
