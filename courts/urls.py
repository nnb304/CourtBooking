from django.urls import path
from . import views

app_name = 'courts'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('court/<int:pk>/', views.court_detail_view, name='court_detail'),
    path('court/<int:pk>/favorite/', views.toggle_favorite_view, name='toggle_favorite'),
    path('favorites/', views.favorite_list_view, name='favorite_list'),
]
