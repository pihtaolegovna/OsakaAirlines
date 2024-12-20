from rest_framework.routers import SimpleRouter
from api import views
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = SimpleRouter()

router.register(r'user', views.UserViewSet, 'User')
router.register(r'client', views.ClientViewSet, 'Client')
router.register(r'flightseat', views.FlightSeatViewSet, 'FlightSeat')
router.register(r'ticket', views.TicketViewSet, 'Ticket')
router.register(r'employee', views.EmployeeViewSet, 'Employee')
router.register(r'boardseat', views.BoardSeatViewSet, 'BoardSeat')
router.register(r'place', views.PlaceViewSet, 'Place')
router.register(r'flight', views.FlightViewSet, 'Flight')
router.register(r'airport', views.AirportViewSet, 'Airport')
router.register(r'board', views.BoardViewSet, 'Board')
router.register(r'model', views.ModelViewSet, 'Model')
router.register(r'manufacturer', views.ManufacturerViewSet, 'Manufacturer')


urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('find_flights/', views.find_flights, name='find_flights'),
    path('book_flight/', views.book_flight, name='book_flight'),
    path('pay_for_flight/', views.pay_for_flight, name='pay_for_flight'),
    path('cancel_flight/', views.cancel_flight, name='cancel_flight'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
