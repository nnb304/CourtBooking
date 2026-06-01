from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/<int:court_id>/', views.booking_create, name='booking_create'),
    path('my/', views.booking_list, name='booking_list'),
    path('owner/', views.owner_booking_list, name='owner_booking_list'),
]
