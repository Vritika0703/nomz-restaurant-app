from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('home/', views.home, name='home'),
    path('role-selection/', views.role_selection, name='role_selection'),
    path('register/<str:role>/', views.register, name='register'),
    path('login/<str:role>/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
