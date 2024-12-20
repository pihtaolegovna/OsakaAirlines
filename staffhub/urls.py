from django.contrib import admin
from django.urls import path, include
from staffhub.views import *
import staffhub.views

app_name = 'staffhub'

urlpatterns = [
    path('flightsmap/', flights_view, name='showflights'),
    path('flights/', flight_management, name='flight_management'),
    path('boards/', board_management, name='board_management'),
    path('flight/<int:flight_id>/', view_flight_with_seat, name='view_flight_with_seat'),
    path('edit-seats/<int:board_id>/', edit_seats_view, name='edit_seats_view'),
    path('model/', model_management, name='model_management'),
    path('manufacturer/', manufacturer_management, name='manufacturer_management'),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),

    path('profile/', user_profile_view, name='profile'),

    path('home/', home, name='home'),
]