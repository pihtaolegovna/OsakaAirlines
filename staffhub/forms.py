# forms.py
from django import forms
from api.models import Model, Flight, Board, Manufacturer, User, Client


class ModelForm(forms.ModelForm):
    class Meta:
        model = Model
        fields = ['name', 'manufacturer']


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput)
    phone = forms.CharField(label="Телефон", max_length=15)  # Поле для телефона

    class Meta:
        model = User
        fields = ['login', 'first_name', 'last_name', 'phone']  # Добавляем поле phone

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()

            # Создаем клиента
            phone = self.cleaned_data["phone"]
            Client.objects.create(user=user, phone=phone, is_deleted=False)

        return user


class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ['name']


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['board_number', 'seats_amount', 'year', 'model']
        widgets = {
            'board_number': forms.TextInput(attrs={'class': 'form-control'}),
            'seats_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'model': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'board_number': 'Board Number',
            'seats_amount': 'Seats Amount',
            'year': 'Year',
            'model': 'Model',
        }


class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = [
            'name', 'board', 'departure_time', 'arrival_time', 'delay_time',
            'gate', 'terminal', 'departure_airport', 'arrival_airport',
            'business_class_price', 'economy_class_price'
        ]

    departure_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'placeholder': 'Select departure time'
        }),
        input_formats=['%Y-%m-%dT%H:%M'],  # Ensuring compatibility with datetime-local input format
    )

    arrival_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'placeholder': 'Select arrival time'
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    delay_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'placeholder': 'Select delay time'
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
        required=False  # Delay time may be optional, so we can set it as not required
    )
