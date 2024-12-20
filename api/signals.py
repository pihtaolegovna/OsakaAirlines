from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Max
from .models import Flight, FlightSeat, Board, BoardSeat

@receiver(post_save, sender=Flight)
def create_flight_seats(sender, instance, created, **kwargs):
    if created:
        # Получаем максимальную версию мест на борту для этого борта
        max_seats_version = BoardSeat.objects.filter(
            board=instance.board
        ).aggregate(max_version=Max('seats_version'))['max_version']

        # Получаем все места на борту с максимальной версией
        board_seats = BoardSeat.objects.filter(
            board=instance.board,
            seats_version=max_seats_version
        )

        print(instance.board)
        print(max_seats_version)
        print(board_seats.count())

        

        # Создаем FlightSeat для каждого места на борту
        for seat in board_seats:
            if seat.seat_type == 'business':
                price = instance.business_class_price
            else:
                price = instance.business_class_price
            FlightSeat.objects.create(
                seat=seat.seat_number,
                row_number=seat.row_number,
                flight=instance,
                status='available',
                price=price,
                is_deleted=False
            )
