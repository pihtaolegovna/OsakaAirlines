from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from api.models import *

@login_required
def cancel_ticket(request, ticket_id):
    try:
        # Get the ticket object
        ticket = get_object_or_404(Ticket, id=ticket_id, client__user=request.user, is_canceled=False, is_deleted=False)
        
        # Get the associated flight seat
        flight_seat = ticket.flight_seat
        
        # Mark the seat as available again
        flight_seat.status = 'available'
        flight_seat.save()

        # Mark the ticket as canceled
        ticket.is_canceled = True
        ticket.save()

        return redirect('staffhub:profile')  # Redirect back to the user's profile page

    except Ticket.DoesNotExist:
        return render(request, 'error.html', {'message': 'Ticket not found or already canceled.'})
    except FlightSeat.DoesNotExist:
        return render(request, 'error.html', {'message': 'Flight seat not found.'})
    except Exception as e:
        return render(request, 'error.html', {'message': f'An unexpected error occurred: {str(e)}'})

def find_flights(request):
    places = Place.objects.all()
    place_names = [place.name for place in places]
    flights = Flight.objects.filter(departure_time__gt=timezone.now(), is_deleted=False)

    if request.method == 'GET' and 'departure' in request.GET and 'arrival' in request.GET:
        departure = request.GET.get('departure')
        arrival = request.GET.get('arrival')

        departure_airports = Airport.objects.filter(place__name__icontains=departure, is_deleted=False)
        arrival_airports = Airport.objects.filter(place__name__icontains=arrival, is_deleted=False)

        

        if departure_airports.exists() and arrival_airports.exists():
            flights = flights.filter(
                departure_airport__in=departure_airports,
                arrival_airport__in=arrival_airports
            )
        else:
            flights = None

    return render(request, 'find_flights.html', {'flights': flights, 'place_names': place_names})


from collections import defaultdict


def select_seat(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id, is_deleted=False)
    all_seats = FlightSeat.objects.filter(flight=flight, is_deleted=False)

    row_based_seats = defaultdict(list)
    for seat in all_seats:
        row_based_seats[seat.row_number].append({
            'seat': seat.seat,
            'status': seat.status,
            'id': seat.id  # Ensure the ID is included
        })

    max_columns = max(len(row) for row in row_based_seats.values())
    column_based_seats = defaultdict(list)
    for row_number, row in row_based_seats.items():
        for col_index in range(max_columns):
            seat_data = row[col_index] if col_index < len(row) else {'seat': '', 'status': 'disabled'}
            column_based_seats[col_index].append(seat_data)

    return render(request, 'select_seat.html', {'flight': flight, 'seats': dict(column_based_seats)})



@login_required
def create_ticket(request, flight_id, seat_id):
    try:
        flight_seat = FlightSeat.objects.get(id=seat_id, flight_id=flight_id, status='available')
        client = Client.objects.get(user=request.user)

        ticket = Ticket.objects.create(client=client, flight_seat=flight_seat)

        flight_seat.status = 'sold'
        flight_seat.save()

        return redirect('staffhub:profile')

    except FlightSeat.DoesNotExist:
        return render(request, 'error.html', {'message': 'Seat not available or already sold.'})
    except Client.DoesNotExist:
        return render(request, 'error.html', {'message': 'Client not found.'})
    except Exception as e:
        return render(request, 'error.html', {'message': f'An unexpected error occurred: {str(e)}'})
