from django.urls import path
from . import views

app_name = 'clienthub'

urlpatterns = [
    path('find-flights/', views.find_flights, name='find_flights'),
    path('select-seat/<int:flight_id>/', views.select_seat, name='select_seat'),
    path('create-ticket/<int:flight_id>/<int:seat_id>/', views.create_ticket, name='create_ticket'),
    path('cancel_ticket/<int:ticket_id>/', views.cancel_ticket, name='cancel_ticket'),
]
