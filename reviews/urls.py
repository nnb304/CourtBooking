from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:court_id>/', views.add_review, name='add_review'),
]
