from django.contrib import admin
from django.urls import path, include
from staffhub.views import *
import adminapp.views
from api.models import *
from .forms import *

app_name = 'adminapp'

MODEL_FORM_MAP = {
    'User': {'model': User, 'form': UserForm},
    'Client': {'model': Client, 'form': ClientForm},
    'Employee': {'model': Employee, 'form': EmployeeForm},
    'FlightSeat': {'model': FlightSeat, 'form': FlightSeatForm},
    'Ticket': {'model': Ticket, 'form': TicketForm},
    'BoardSeat': {'model': BoardSeat, 'form': BoardSeatForm},
    'Place': {'model': Place, 'form': PlaceForm},
    'Airport': {'model': Airport, 'form': AirportForm},
    'Flight': {'model': Flight, 'form': FlightForm},
    'Board': {'model': Board, 'form': BoardForm},
    'Model': {'model': Model, 'form': ModelForm},
    'Manufacturer': {'model': Manufacturer, 'form': ManufacturerForm},
}

BOARD_FORM_MAP = {
    'BoardSeat': {'model': BoardSeat, 'form': BoardSeatForm},
    'Place': {'model': Place, 'form': PlaceForm},
    'Airport': {'model': Airport, 'form': AirportForm},
    'Board': {'model': Board, 'form': BoardForm},
    'Model': {'model': Model, 'form': ModelForm},
    'Manufacturer': {'model': Manufacturer, 'form': ManufacturerForm},
}

FLIGHT_FORM_MAP = {
    'FlightSeat': {'model': FlightSeat, 'form': FlightSeatForm},
    'Ticket': {'model': Ticket, 'form': TicketForm},
    'BoardSeat': {'model': BoardSeat, 'form': BoardSeatForm},
    'Place': {'model': Place, 'form': PlaceForm},
    'Flight': {'model': Flight, 'form': FlightForm},
}

urlpatterns = [
    # Admin dashboard
    path('dashboard/', adminapp.views.generic_dashboard, 
         {'model_form_map': MODEL_FORM_MAP, 'is_verbose': False}, name='dashboard'),

    path('backups/', adminapp.views.manage_backups, name='manage_backups'),

    # Flight management
    path('flight_managements/', adminapp.views.generic_dashboard, 
         {'model_form_map': FLIGHT_FORM_MAP, 'is_verbose': True}, name='flight_managements'),

    # Board management
    path('board_managements/', adminapp.views.generic_dashboard, 
         {'model_form_map': BOARD_FORM_MAP, 'is_verbose': True}, name='board_managements'),
]
