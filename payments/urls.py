from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('pay/<int:booking_id>/', views.payment_process, name='payment_process'),
]
