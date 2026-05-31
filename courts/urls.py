from django.urls import path
from . import views

app_name = 'courts'

urlpatterns = [
    path('', views.court_list, name='court_list'),
    path('court/<int:pk>/', views.court_detail, name='court_detail'),
    path('court/<int:pk>/favorite/', views.toggle_favorite_view, name='toggle_favorite'),
    path('favorites/', views.favorite_list_view, name='favorite_list'),
]
