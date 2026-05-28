from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/<int:court_id>/', views.booking_create_view, name='booking_create'),
    path('my/', views.my_bookings_view, name='my_bookings'),
]
