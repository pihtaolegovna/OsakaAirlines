from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from .forms import ModelForm, ManufacturerForm, BoardForm, FlightForm
import json
from django.utils import timezone
from django.core.paginator import Paginator
from api.models import Ticket, Flight, FlightSeat, Airport, Board, BoardSeat, Model, Manufacturer, Client, Employee
from django.db.models import Q
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import models
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Max
from .forms import UserRegistrationForm


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('staffhub:home')  # Redirect to dashboard after login
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('staffhub:login')  # Redirect to login page after logout


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аккаунт успешно создан! Вы можете войти в систему.')
            return redirect('staffhub:login')  # Перенаправление на страницу входа после регистрации
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


def view_flight_with_seat(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    flight_seats = FlightSeat.objects.filter(flight=flight)
    tickets = Ticket.objects.filter(
        flight_seat__flight=flight, is_deleted=False
    ).select_related(
        'client__user',
        'flight_seat__flight',
        'flight_seat__flight__departure_airport',
        'flight_seat__flight__arrival_airport',
    )
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page', 1)
    tickets_page = paginator.get_page(page_number)

    def row_number_to_letter(row_number):
        return chr(64 + row_number)
    rows = flight_seats.values_list('row_number', flat=True).distinct()
    columns = flight_seats.filter(row_number=rows[0]).count() if rows else 0

    threshold_price = flight_seats.aggregate(models.Max('price'))['price__max'] * 0.8  # 80% of the highest price as threshold for business class
    business_class_seats = flight_seats.filter(price__gte=threshold_price)
    business_class_rows = business_class_seats.values_list('row_number', flat=True).distinct()

    context = {
        'flight': flight,
        'flight_seats': flight_seats,
        'tickets': tickets_page,
        'paginator': paginator,
        'rows_count': len(rows),
        'columns_count': columns,
        'business_class_row_count': len(business_class_rows),
    }

    return render(request, 'ViewFlightWithseat.html', context)


def flight_management(request):
    filter_query = request.GET.get('filter', '')
    date_filter = request.GET.get('date_filter', 'all')
    status_filter = request.GET.get('status_filter', '')  # Added status filter
    sort_by = request.GET.get('sort', 'id')  # Default sort by ID
    order = request.GET.get('order', 'asc')  # Default order is ascending

    flights = Flight.objects.all()

    if filter_query:
        flights = flights.filter(
            Q(board__board_number__icontains=filter_query) |
            Q(departure_airport__name__icontains=filter_query) |
            Q(arrival_airport__name__icontains=filter_query) |
            Q(delay_time__icontains=filter_query)
        )

    now = datetime.now()
    if date_filter == 'future':
        flights = flights.filter(departure_time__gte=now)
    elif date_filter == 'past':
        flights = flights.filter(departure_time__lt=now)

    if status_filter:
        flights = flights.filter(status=status_filter)

    flights = flights.order_by(f'{"" if order == "asc" else "-"}{sort_by}')

    if request.method == 'POST':
        if 'create_flight' in request.POST:
            form = FlightForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('flight_management')
        
        elif 'edit_flight' in request.POST:
            flight = get_object_or_404(Flight, id=request.POST.get('flight_id'))
            form = FlightForm(request.POST, instance=flight)
            if form.is_valid():
                form.save()
                return redirect('flight_management')

        elif 'delete_flight' in request.POST:
            flight = get_object_or_404(Flight, id=request.POST.get('flight_id'))
            flight.delete()
            return redirect('flight_management')

        elif 'multi_delete' in request.POST:
            ids = request.POST.getlist('ids')
            Flight.objects.filter(id__in=ids).delete()
            return redirect('flight_management')

    # Get all airports and boards for the form options
    airports = Airport.objects.all()
    boards = Board.objects.all()

    # Set up pagination for flights
    paginator = Paginator(flights, 10)
    page_number = request.GET.get('page', 1)
    flights = paginator.get_page(page_number)

    context = {
        'flights': flights,
        'create_form': FlightForm(),
        'airports': airports,
        'page_number': page_number,
        'paginator': paginator,
        'date_filter': date_filter,
        'status_filter': status_filter,
        'boards': boards,
        'sort': sort_by,
        'order': order
    }

    return render(request, 'FlightPage.html', context)


def home(request):
    return render(request, 'home.html')


@login_required
def user_profile_view(request):
    user = request.user
    try:
        client = user.client  # Accessing the related client
    except Client.DoesNotExist:
        client = None

    try:
        employee = user.employee  # Accessing the related client
    except Employee.DoesNotExist:
        employee = None

    # Fetch upcoming and past flights
    current_time = timezone.now()
    upcoming_flights = Flight.objects.filter(departure_time__gte=current_time).exclude(is_deleted=True)

    # Filter only flights the user has tickets for
    user_tickets = Ticket.objects.filter(client=client, is_canceled=False, is_deleted=False)
    user_upcoming_flights = upcoming_flights.filter(id__in=user_tickets.values_list('flight_seat__flight', flat=True))

    past_flights = Flight.objects.filter(departure_time__lt=current_time).exclude(is_deleted=True)
    user_past_flights = past_flights.filter(id__in=user_tickets.values_list('flight_seat__flight', flat=True))

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.middle_name = request.POST.get('middle_name', user.middle_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        if client:
            client.phone = request.POST.get('phone', client.phone)
        if employee:
            employee.email = request.POST.get('email', employee.email)
        user.is_dark_theme = request.POST.get('is_dark_theme') == 'True'
        user.accent_color = request.POST.get('accent_color', user.accent_color)
        user.is_transparent = request.POST.get('is_transparent', user.is_transparent)
        user.is_active = request.POST.get('is_active') == 'True'
        user.save()
        if client:
            client.save()
        if employee:
            employee.save()

        return HttpResponseRedirect(reverse('staffhub:profile'))

    return render(
        request,
        'profile.html',
        {
            'user': user,
            'client': client,  # Pass client to the template
            'upcoming_flights': user_upcoming_flights,  # Only flights the user has tickets for
            'past_flights': user_past_flights,          # Only past flights the user has tickets for
            'tickets': user_tickets,  # Pass tickets to the template
        }
    )


def flights_view(request):
    flights = Flight.objects.all()
    flight_data = []

    for flight in flights:
        duration = (flight.arrival_time - flight.departure_time).total_seconds() / 60

        if flight.departure_time <= timezone.now() <= flight.arrival_time:
            elapsed_time = (timezone.now() - flight.departure_time).total_seconds() / 60
        else:
            elapsed_time = 0

        flight_info = {
            'id': flight.id,
            'departure_place': {
                'name': flight.departure_airport.place.name,
                'latitude': float(flight.departure_airport.place.latitude),
                'longitude': float(flight.departure_airport.place.longitude),
            },
            'arrival_place': {
                'name': flight.arrival_airport.place.name,
                'latitude': float(flight.arrival_airport.place.latitude),
                'longitude': float(flight.arrival_airport.place.longitude),
            },
            'elapsed_time': elapsed_time,
            'duration': duration,
        }
        flight_data.append(flight_info)

    return render(request, 'flights.html', {'flight_data': json.dumps(flight_data)})


def edit_seats_view(request, board_id):
    board = get_object_or_404(Board, pk=board_id)

    if request.method == 'POST':
        try:
            rows = int(request.POST.get('rows', 0))
        except ValueError:
            rows = 0 
        try:
            seats = int(request.POST.get('seats', 0))  
        except ValueError:
            seats = 0  
        try:
            business_seats = int(request.POST.get('business', 0))  
        except ValueError:
            business_seats = 0  
        current_version = BoardSeat.objects.filter(board=board).aggregate(Max('seats_version'))['seats_version__max'] or 0
        new_version = current_version + 1

        BoardSeat.objects.filter(board=board, seats_version=new_version).delete()

        for row_number in range(1, seats + 1):
            for seat_number in range(1, rows + 1):
                seat_type = 'Business' if row_number <= business_seats else 'Economy'
                BoardSeat.objects.create(
                    board=board,
                    seat_type=seat_type,
                    row_number=seat_number,
                    seat_number=row_number,
                    seats_version=new_version,
                    is_deleted=False
                )

        return redirect('staffhub:home')

    latest_version = BoardSeat.objects.filter(board=board).aggregate(Max('seats_version'))['seats_version__max']
    board_seats = BoardSeat.objects.filter(board=board, seats_version=latest_version, is_deleted=False)
    seat_layout = {}
    for seat in board_seats:
        if seat.row_number not in seat_layout:
            seat_layout[seat.row_number] = []
        seat_layout[seat.row_number].append({
            'seat_number': seat.seat_number,
            'seat_type': seat.seat_type,
            'status': 'available',
        })

    rows = board_seats.values('row_number').distinct().count()
    seats_per_row = max(board_seats.filter(row_number=1).values_list('seat_number', flat=True), default=0)

    try:
        result = board_seats.filter(seat_type='Business').count() // rows,
    except ZeroDivisionError:
        result = 0

    context = {
        'seat_layout': seat_layout,
        'board': board,
        'rows': rows,
        'seats_per_row': seats_per_row,
        'result': result,
    }

    return render(request, 'edit_seats.html', context)


def board_management(request):
    filter_query = request.GET.get('filter', '')
    status_filter = request.GET.get('status', '')
    model_filter = request.GET.get('model', '')

    boards = Board.objects.all()

    if filter_query:
        boards = boards.filter(board_number__icontains=filter_query)

    if status_filter == 'active':
        boards = boards.filter(is_deleted=False)
    elif status_filter == 'inactive':
        boards = boards.filter(is_deleted=True)

    if model_filter:
        boards = boards.filter(model_id=model_filter)

    paginator = Paginator(boards, 10) 
    page_number = request.GET.get('page')
    paged_boards = paginator.get_page(page_number)

    if request.method == 'POST':
        if 'create_board' in request.POST:
            create_form = BoardForm(request.POST)
            if create_form.is_valid():
                create_form.save()
                return redirect('board_management')
        elif 'edit_board' in request.POST:
            board_id = request.POST.get('board_id')
            board = get_object_or_404(Board, pk=board_id)
            edit_form = BoardForm(request.POST, instance=board)
            if edit_form.is_valid():
                edit_form.save()
                return redirect('board_management')
        elif 'delete_board' in request.POST:
            board_id = request.POST.get('board_id')
            board = get_object_or_404(Board, pk=board_id)
            board.is_deleted = True
            board.save()
            return redirect('board_management')
        elif 'multi_delete' in request.POST:
            ids_to_delete = request.POST.getlist('ids')
            Board.objects.filter(id__in=ids_to_delete).update(is_deleted=True)
            return redirect('board_management')

    create_form = BoardForm()
    edit_form = BoardForm()
    models = Model.objects.all()

    context = {
        'boards': paged_boards,
        'create_form': create_form,
        'edit_form': edit_form,
        'models': models,
        'paginator': paginator,
        'page_number': page_number,
    }

    return render(request, 'BoardPage.html', context)


def model_management(request):
    filter_query = request.GET.get('filter', '')
    status_filter = request.GET.get('status', '')
    manufacturer_filter = request.GET.get('manufacturer', '')

    models = Model.objects.all()

    if filter_query:
        models = models.filter(name__icontains=filter_query)

    if status_filter == 'active':
        models = models.filter(is_deleted=False)
    elif status_filter == 'inactive':
        models = models.filter(is_deleted=True)

    if manufacturer_filter:
        models = models.filter(manufacturer_id=manufacturer_filter)

    paginator = Paginator(models, 10) 
    page_number = request.GET.get('page')
    paged_models = paginator.get_page(page_number)

    if request.method == 'POST':
        if 'create_model' in request.POST:
            create_form = ModelForm(request.POST)
            if create_form.is_valid():
                create_form.save()
                return redirect('model_management')
        elif 'edit_model' in request.POST:
            model_id = request.POST.get('model_id')
            model = get_object_or_404(Model, pk=model_id)
            edit_form = ModelForm(request.POST, instance=model)
            if edit_form.is_valid():
                edit_form.save()
                return redirect('model_management')
        elif 'delete_model' in request.POST:
            model_id = request.POST.get('model_id')
            model = get_object_or_404(Model, pk=model_id)
            model.is_deleted = True
            model.save()
            return redirect('model_management')
        elif 'multi_delete' in request.POST:
            ids_to_delete = request.POST.getlist('ids')
            Model.objects.filter(id__in=ids_to_delete).update(is_deleted=True)
            return redirect('model_management')

    create_form = ModelForm()
    edit_form = ModelForm()
    manufacturers = Manufacturer.objects.all()

    context = {
        'models': paged_models,
        'create_form': create_form,
        'edit_form': edit_form,
        'manufacturers': manufacturers,
        'paginator': paginator,
        'page_number': page_number,
    }

    return render(request, 'ModelPage.html', context)


def manufacturer_management(request):
    filter_query = request.GET.get('filter', '')
    status_filter = request.GET.get('status', '')

    manufacturers = Manufacturer.objects.all()

    if filter_query:
        manufacturers = manufacturers.filter(name__icontains=filter_query)

    if status_filter == 'active':
        manufacturers = manufacturers.filter(is_active=True)
    elif status_filter == 'inactive':
        manufacturers = manufacturers.filter(is_active=False)

    if request.method == 'POST':
        if 'create_manufacturer' in request.POST:
            form = ManufacturerForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('manufacturer_management')

        elif 'edit_manufacturer' in request.POST:
            manufacturer = get_object_or_404(Manufacturer, id=request.POST.get('manufacturer_id'))
            form = ManufacturerForm(request.POST, instance=manufacturer)
            if form.is_valid():
                form.save()
                return redirect('manufacturer_management')

        elif 'delete_manufacturer' in request.POST:
            manufacturer = get_object_or_404(Manufacturer, id=request.POST.get('manufacturer_id'))
            manufacturer.delete()
            return redirect('manufacturer_management')

        elif 'multi_delete' in request.POST:
            ids = request.POST.getlist('ids')
            Manufacturer.objects.filter(id__in=ids).delete()
            return redirect('manufacturer_management')

    paginator = Paginator(manufacturers, 10)
    page_number = request.GET.get('page', 1)
    manufacturers = paginator.get_page(page_number)

    context = {
        'manufacturers': manufacturers,
        'create_form': ManufacturerForm(),
        'page_number': page_number,
        'paginator': paginator
    }
    return render(request, 'ManufacturerPage.html', context)
