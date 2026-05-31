from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:court_id>/', views.review_create, name='review_create'),
]
