from django.contrib import admin
from .models import (
    User, Client, Employee, FlightSeat, Ticket, BoardSeat, 
    Place, Airport, Flight, Board, Model, Manufacturer
)

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'login', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('login',)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'user', 'is_deleted')
    list_filter = ('is_deleted',)
    search_fields = ('phone', 'user__login')

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'is_deleted')
    list_filter = ('is_deleted',)
    search_fields = ('email', 'user__login')

class FlightSeatAdmin(admin.ModelAdmin):
    list_display = ('id', 'seat', 'flight', 'status', 'price', 'is_deleted')
    list_filter = ('status', 'is_deleted')
    search_fields = ('seat', 'flight__id')

class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'flight_seat', 'is_deleted', 'is_canceled', 'is_paid')
    list_filter = ('is_deleted', 'is_canceled', 'is_paid')
    search_fields = ('client__user__login', 'flight_seat__seat')

class BoardSeatAdmin(admin.ModelAdmin):
    list_display = ('id', 'board', 'seat_type', 'row_number', 'seat_number', 'is_deleted', 'seats_version')
    list_filter = ('is_deleted', 'seat_type')
    search_fields = ('board__board_number', 'row_number', 'seat_number')

class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'latitude', 'longitude', 'is_deleted')
    list_filter = ('is_deleted',)
    search_fields = ('name',)

class AirportAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'place', 'is_deleted')
    list_filter = ('is_deleted',)
    search_fields = ('name', 'place__name')

class FlightAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'board', 'departure_time', 'arrival_time', 'delay_time', 
        'gate', 'terminal', 'departure_airport', 'arrival_airport', 'is_deleted'
    )
    list_filter = ('is_deleted', 'departure_airport', 'arrival_airport')
    search_fields = ('departure_airport__name', 'arrival_airport__name', 'board__board_number')

class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'model', 'board_number', 'year', 'seats_amount', 'is_deleted')
    list_filter = ('is_deleted', 'year')
    search_fields = ('board_number', 'model__name')

class ModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'manufacturer', 'name', 'is_deleted')
    list_filter = ('is_deleted',)
    search_fields = ('name', 'manufacturer__name')

class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_deleted')
    list_filter = ('is_deleted',)
    search_fields = ('name',)

# Регистрация всех моделей
admin.site.register(User, CustomUserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(FlightSeat, FlightSeatAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(BoardSeat, BoardSeatAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Airport, AirportAdmin)
admin.site.register(Flight, FlightAdmin)
admin.site.register(Board, BoardAdmin)
admin.site.register(Model, ModelAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
