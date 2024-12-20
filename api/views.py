from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from api.serializers import UserSerializer, ClientSerializer, FlightSeatSerializer, TicketSerializer, EmployeeSerializer, BoardSeatSerializer, PlaceSerializer, FlightSerializer, AirportSerializer, BoardSerializer, ModelSerializer, ManufacturerSerializer
from api.models import User, Client, FlightSeat, Ticket, Employee, BoardSeat, Place, Flight, Airport, Board, Model, Manufacturer
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view
from django.utils.dateparse import parse_datetime

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            client_data = request.data.get('client', {})
            client_serializer = ClientSerializer(data={**client_data, 'user': user.id})
            if client_serializer.is_valid():
                client_serializer.save()
                return Response({"message": "User and Client created successfully"}, status=status.HTTP_201_CREATED)
            return Response(client_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def find_flights(request):
    departure_place = request.query_params.get('departure_place')
    arrival_place = request.query_params.get('arrival_place')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    try:
        if start_date:
            start_date = parse_datetime(start_date)
        if end_date:
            end_date = parse_datetime(end_date)
        
        flights = Flight.objects.filter(
            departure_airport__place__name=departure_place,
            arrival_airport__place__name=arrival_place,
            departure_time__range=(start_date, end_date) if start_date and end_date else (None, None)
        )
        flight_serializer = FlightSerializer(flights, many=True)
        return Response(flight_serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def book_flight(request):
    client_id = request.data.get('client_id')
    flight_seat_id = request.data.get('flight_seat_id')

    try:
        client = Client.objects.get(id=client_id, is_deleted=False)
        flight_seat = FlightSeat.objects.get(id=flight_seat_id, status='available', is_deleted=False)

        ticket = Ticket.objects.create(client=client, flight_seat=flight_seat)
        flight_seat.status = 'sold'
        flight_seat.save()

        ticket_serializer = TicketSerializer(ticket)
        return Response(ticket_serializer.data, status=status.HTTP_201_CREATED)
    except Client.DoesNotExist:
        return Response({"error": "Client not found or deleted"}, status=status.HTTP_400_BAD_REQUEST)
    except FlightSeat.DoesNotExist:
        return Response({"error": "Flight seat not available or deleted"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def pay_for_flight(request):
    ticket_id = request.data.get('ticket_id')
    try:
        ticket = Ticket.objects.get(id=ticket_id, is_paid=False)
        ticket.is_paid = True
        ticket.save()
        return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)
    except Ticket.DoesNotExist:
        return Response({"error": "Ticket not found or already paid"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def cancel_flight(request):
    ticket_id = request.data.get('ticket_id')
    try:
        ticket = Ticket.objects.get(id=ticket_id, is_canceled=False)
        ticket.is_canceled = True
        ticket.save()

        flight_seat = ticket.flight_seat
        flight_seat.status = 'available'
        flight_seat.save()

        return Response({"message": "Flight canceled successfully"}, status=status.HTTP_200_OK)
    except Ticket.DoesNotExist:
        return Response({"error": "Ticket not found or already canceled"}, status=status.HTTP_400_BAD_REQUEST)



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(ViewSet):

    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = User.objects.order_by('pk')
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=404)
        serializer = UserSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class ClientViewSet(ViewSet):

    def list(self, request):
        queryset = Client.objects.order_by('pk')
        serializer = ClientSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = Client.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = ClientSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response(status=404)
        serializer = ClientSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class FlightSeatViewSet(ViewSet):

    def list(self, request):
        queryset = FlightSeat.objects.order_by('pk')
        serializer = FlightSeatSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = FlightSeatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = FlightSeat.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = FlightSeatSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = FlightSeat.objects.get(pk=pk)
        except FlightSeat.DoesNotExist:
            return Response(status=404)
        serializer = FlightSeatSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = FlightSeat.objects.get(pk=pk)
        except FlightSeat.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class TicketViewSet(ViewSet):

    def list(self, request):
        queryset = Ticket.objects.order_by('pk')
        serializer = TicketSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = Ticket.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = TicketSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response(status=404)
        serializer = TicketSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class EmployeeViewSet(ViewSet):

    def list(self, request):
        queryset = Employee.objects.order_by('pk')
        serializer = EmployeeSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = Employee.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = EmployeeSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return Response(status=404)
        serializer = EmployeeSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class BoardSeatViewSet(ViewSet):

    def list(self, request):
        queryset = BoardSeat.objects.order_by('pk')
        serializer = BoardSeatSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = BoardSeatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = BoardSeat.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = BoardSeatSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = BoardSeat.objects.get(pk=pk)
        except BoardSeat.DoesNotExist:
            return Response(status=404)
        serializer = BoardSeatSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = BoardSeat.objects.get(pk=pk)
        except BoardSeat.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class PlaceViewSet(ViewSet):

    def list(self, request):
        queryset = Place.objects.order_by('pk')
        serializer = PlaceSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = PlaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = Place.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = PlaceSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = Place.objects.get(pk=pk)
        except Place.DoesNotExist:
            return Response(status=404)
        serializer = PlaceSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = Place.objects.get(pk=pk)
        except Place.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class FlightViewSet(ViewSet):

    def list(self, request):
        queryset = Flight.objects.order_by('pk')
        serializer = FlightSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = FlightSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = Flight.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = FlightSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = Flight.objects.get(pk=pk)
        except Flight.DoesNotExist:
            return Response(status=404)
        serializer = FlightSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = Flight.objects.get(pk=pk)
        except Flight.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class AirportViewSet(ViewSet):

    def list(self, request):
        queryset = Airport.objects.order_by('pk')
        serializer = AirportSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = AirportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = Airport.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = AirportSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = Airport.objects.get(pk=pk)
        except Airport.DoesNotExist:
            return Response(status=404)
        serializer = AirportSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = Airport.objects.get(pk=pk)
        except Airport.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class BoardViewSet(ViewSet):

    def list(self, request):
        queryset = Board.objects.order_by('pk')
        serializer = BoardSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = BoardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = Board.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = BoardSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            return Response(status=404)
        serializer = BoardSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class ModelViewSet(ViewSet):

    def list(self, request):
        queryset = Model.objects.order_by('pk')
        serializer = ModelSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = Model.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = ModelSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = Model.objects.get(pk=pk)
        except Model.DoesNotExist:
            return Response(status=404)
        serializer = ModelSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = Model.objects.get(pk=pk)
        except Model.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class ManufacturerViewSet(ViewSet):

    def list(self, request):
        queryset = Manufacturer.objects.order_by('pk')
        serializer = ManufacturerSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ManufacturerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = Manufacturer.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = ManufacturerSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = Manufacturer.objects.get(pk=pk)
        except Manufacturer.DoesNotExist:
            return Response(status=404)
        serializer = ManufacturerSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = Manufacturer.objects.get(pk=pk)
        except Manufacturer.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)
