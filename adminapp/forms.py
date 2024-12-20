from django import forms
from api.models import User, Client, Employee, FlightSeat, Ticket, BoardSeat, Place, Airport, Flight, Board, Model, Manufacturer
from django.contrib.auth.hashers import make_password


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['login', 'password', 'role', 'is_active', 'is_staff', 'is_dark_theme', 'is_transparent', 'accent_color', 'first_name', 'middle_name', 'last_name']
        widgets = {
            'password': forms.PasswordInput(),
            'role': forms.Select(choices=User.ROLE_CHOICES),
            'is_dark_theme': forms.CheckboxInput(),
            'is_transparent': forms.CheckboxInput(),
            'accent_color': forms.TextInput(attrs={'type': 'color'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.password:
            user.password = make_password(user.password)
        if commit:
            user.save()
        return user


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['phone', 'user', 'is_deleted']
        widgets = {
            'is_deleted': forms.CheckboxInput(),
            'user': forms.Select(),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['email', 'user', 'is_deleted']
        widgets = {
            'is_deleted': forms.CheckboxInput(),
            'user': forms.Select(),
        }


class FlightSeatForm(forms.ModelForm):
    class Meta:
        model = FlightSeat
        fields = ['seat', 'row_number', 'flight', 'status', 'price', 'is_deleted']
        widgets = {
            'status': forms.Select(choices=FlightSeat.STATUS_CHOICES),
            'price': forms.NumberInput(),
            'is_deleted': forms.CheckboxInput(),
            'flight': forms.Select(),
        }


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['client', 'flight_seat', 'is_deleted', 'is_canceled', 'is_paid']
        widgets = {
            'is_deleted': forms.CheckboxInput(),
            'client': forms.Select(),
            'flight_seat': forms.Select(),
        }


class BoardSeatForm(forms.ModelForm):
    class Meta:
        model = BoardSeat
        fields = ['board', 'seat_type', 'row_number', 'seat_number', 'is_deleted', 'seats_version']
        widgets = {
            'is_deleted': forms.CheckboxInput(),
            'seat_type': forms.Select(choices=BoardSeat.SEAT_TYPE_CHOICES),
            'board': forms.Select(),
        }

class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ['name', 'latitude', 'longitude', 'is_deleted']
        widgets = {
            'latitude': forms.NumberInput(attrs={'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'step': 'any'}),
            'is_deleted': forms.CheckboxInput(),
        }




class AirportForm(forms.ModelForm):
    class Meta:
        model = Airport
        fields = ['place', 'name', 'full_name', 'is_deleted']
        widgets = {
            'is_deleted': forms.CheckboxInput(),
            'place': forms.Select(),
        }


class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = ['name', 'board', 'departure_time', 'arrival_time', 'delay_time', 'gate', 'terminal', 'departure_airport', 'arrival_airport', 'is_deleted', 'business_class_price', 'economy_class_price']
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'delay_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'business_class_price': forms.NumberInput(),
            'economy_class_price': forms.NumberInput(),
            'is_deleted': forms.CheckboxInput(),
            'departure_airport': forms.Select(),
            'arrival_airport': forms.Select(),
            'board': forms.Select(),
        }


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['model', 'board_number', 'year', 'seats_amount', 'is_deleted']
        widgets = {
            'model': forms.Select(),
            'is_deleted': forms.CheckboxInput(),
        }


class ModelForm(forms.ModelForm):
    class Meta:
        model = Model
        fields = ['manufacturer', 'name', 'is_deleted']
        widgets = {
            'manufacturer': forms.Select(),
            'is_deleted': forms.CheckboxInput(),
        }


class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ['name', 'is_deleted']
        widgets = {
            'is_deleted': forms.CheckboxInput(),
        }
