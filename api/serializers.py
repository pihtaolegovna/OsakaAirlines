from rest_framework.serializers import ModelSerializer
from api.models import Client, FlightSeat, Ticket, Employee, BoardSeat, Place, Flight, Airport, Board, Model, Manufacturer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from api.models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        login = attrs.get('username')

        try:
            # Adjust to check for 'login' instead of 'username'
            user = User.objects.get(login=login)
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found')

        attrs['username'] = user.login
        return super().validate(attrs)

class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class ClientSerializer(ModelSerializer):

    class Meta:
        model = Client
        fields = '__all__'


class FlightSeatSerializer(ModelSerializer):

    class Meta:
        model = FlightSeat
        fields = '__all__'


class TicketSerializer(ModelSerializer):

    class Meta:
        model = Ticket
        fields = '__all__'


class EmployeeSerializer(ModelSerializer):

    class Meta:
        model = Employee
        fields = '__all__'


class BoardSeatSerializer(ModelSerializer):

    class Meta:
        model = BoardSeat
        fields = '__all__'


class PlaceSerializer(ModelSerializer):

    class Meta:
        model = Place
        fields = '__all__'


class FlightSerializer(ModelSerializer):

    class Meta:
        model = Flight
        fields = '__all__'


class AirportSerializer(ModelSerializer):

    class Meta:
        model = Airport
        fields = '__all__'


class BoardSerializer(ModelSerializer):

    class Meta:
        model = Board
        fields = '__all__'


class ModelSerializer(ModelSerializer):

    class Meta:
        model = Model
        fields = '__all__'


class ManufacturerSerializer(ModelSerializer):

    class Meta:
        model = Manufacturer
        fields = '__all__'
