from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.auth.models import BaseUserManager
from encrypted_model_fields.fields import EncryptedCharField
from django.contrib.auth.models import User



class CustomUserManager(BaseUserManager):
    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise ValueError('The Login field must be set')
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(login, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('admin', 'Admin'),
        ('fired', 'Fired'),
        ('revenue', 'Revenue Manager'),
        ('flight', 'Flight Manager'),
        ('board', 'Board Manager'),
        ('unassigned', 'Unassigned'),
    ]

    first_name = EncryptedCharField(max_length=100, null=True, blank=True)
    middle_name = EncryptedCharField(max_length=100, null=True, blank=True)
    last_name = EncryptedCharField(max_length=100, null=True, blank=True)
    login = models.CharField(max_length=12, unique=True, verbose_name="Логин")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Роль")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Сотрудник")
    is_dark_theme = models.BooleanField(default=False, verbose_name="Темная тема")
    is_transparent = models.BooleanField(default=False, verbose_name="Прозрачный интерфейс")
    accent_color = models.CharField(max_length=7, default='#7d0e85', verbose_name="Цвет акцента")

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',
        blank=True,
        verbose_name="Группы"
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_user_permissions',
        blank=True,
        verbose_name="Права пользователя"
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.login

    def get_model_name(self):
        return self.__class__.__name__

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'



class Client(models.Model):
    phone = EncryptedCharField(max_length=15, verbose_name="Телефон")
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")

    def get_model_name(self):
        return self.__class__.__name__

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    email = models.EmailField(verbose_name="Электронная почта")
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")

    def get_model_name(self):
        return self.__class__.__name__

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'


class FlightSeat(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled'),
        ('disabled', 'Disabled'),
    ]

    id = models.AutoField(primary_key=True)
    seat = models.IntegerField(verbose_name="Место")
    row_number = models.IntegerField(verbose_name="Номер ряда")
    flight = models.ForeignKey('Flight', on_delete=models.CASCADE, verbose_name="Рейс")
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, verbose_name="Статус")
    price = models.FloatField(verbose_name="Цена")
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")

    def row_letter(self):
        return chr(64 + self.row_number)  # 65 in ASCII is 'A'

    def __str__(self):
        return f"{self.seat}{self.row_number}"

    def get_model_name(self):
        return self.__class__.__name__

    class Meta:
        verbose_name = 'Место на рейсе'
        verbose_name_plural = 'Места на рейсах'


class Ticket(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    flight_seat = models.ForeignKey(FlightSeat, on_delete=models.CASCADE, verbose_name="Место на рейсе")
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")
    is_canceled = models.BooleanField(default=False, verbose_name="Отменен")
    is_paid = models.BooleanField(default=False, verbose_name="Оплачен")

    def get_model_name(self):
        return self.__class__.__name__

    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'


class BoardSeat(models.Model):
    board = models.ForeignKey('Board', on_delete=models.CASCADE, verbose_name="Борт")
    seat_type = models.CharField(max_length=20, verbose_name="Тип места") 
    row_number = models.IntegerField(verbose_name="Номер ряда")
    seat_number = models.IntegerField(verbose_name="Номер места")
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")
    seats_version = models.IntegerField(verbose_name="Версия мест")

    SEAT_TYPE_CHOICES = [
        ('Economy', 'Economy'),
        ('Business', 'Business'),
    ]

    def get_model_name(self):
        return self.__class__.__name__

    class Meta:
        verbose_name = 'Место на борту'
        verbose_name_plural = 'Места на борту'


class Place(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.000000, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.000000, verbose_name="Долгота")
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")

    def __str__(self):
        return self.name

    def get_model_name(self):
        return self.__class__.__name__

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'


class Airport(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, verbose_name="Место")
    name = models.CharField(max_length=100, verbose_name="Название")
    full_name = models.CharField(max_length=100, verbose_name="Полное название")
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")

    def __str__(self):
        return f"{self.name} ({self.place.name})"

    def get_model_name(self):
        return self.__class__.__name__

    class Meta:
        verbose_name = 'Аэропорт'
        verbose_name_plural = 'Аэропорты'


class Flight(models.Model):
    name = models.CharField(max_length=10, null=True, blank=True, verbose_name="Название")
    board = models.ForeignKey('Board', on_delete=models.CASCADE, verbose_name="Борт")
    departure_time = models.DateTimeField(verbose_name="Время вылета")
    arrival_time = models.DateTimeField(verbose_name="Время прилета")
    delay_time = models.DateTimeField(null=True, blank=True, verbose_name="Время задержки")
    gate = models.CharField(max_length=10, null=True, blank=True, verbose_name="Выход")
    terminal = models.CharField(max_length=10, null=True, blank=True, verbose_name="Терминал")
    departure_airport = models.ForeignKey(Airport, related_name='departure_flights', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Аэропорт отправления")
    arrival_airport = models.ForeignKey(Airport, related_name='arrival_flights', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Аэропорт прибытия")
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")
    business_class_price = models.FloatField(default=0.0, verbose_name="Цена бизнес класса")
    economy_class_price = models.FloatField(default=0.0, verbose_name="Цена эконом класса")

    def __str__(self):
        departure_airport = self.departure_airport.name if self.departure_airport else "Unknown Departure"
        arrival_airport = self.arrival_airport.name if self.arrival_airport else "Unknown Arrival"
        return f"Flight from {departure_airport} to {arrival_airport}"

    def get_model_name(self):
        return self.__class__.__name__

    class Meta:
        verbose_name = 'Рейс'
        verbose_name_plural = 'Рейсы'


class Board(models.Model):
    model = models.ForeignKey('Model', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Модель")
    board_number = models.CharField(max_length=50, verbose_name="Номер борта")
    year = models.IntegerField(verbose_name="Год выпуска")
    seats_amount = models.IntegerField(verbose_name="Количество мест")
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")

    def __str__(self):
        if self.model and self.model.manufacturer:
            return f"{self.model.manufacturer.name} {self.model.name} {self.board_number}"
        return f"Board {self.board_number}"

    def get_model_name(self):
        return self.__class__.__name__

    class Meta:
        verbose_name = 'Борт'
        verbose_name_plural = 'Борты'


class Model(models.Model):
    manufacturer = models.ForeignKey('Manufacturer', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Производитель")
    name = models.CharField(max_length=100, verbose_name="Название модели")
    is_deleted = models.BooleanField(default=False, verbose_name="Удалена")

    def __str__(self):
        if self.manufacturer:
            return f"{self.manufacturer.name} {self.name}"
        return f"Model {self.name} (no manufacturer)"

    def get_model_name(self):
        return self.__class__.__name__

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'


class Manufacturer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название производителя")
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")

    def __str__(self):
        return self.name

    def get_model_name(self):
        return self.__class__.__name__

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'
