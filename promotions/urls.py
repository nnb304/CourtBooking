from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('',                  views.promotion_list,    name='promotion_list'),
    path('add/',              views.promotion_create,  name='promotion_create'),
    path('edit/<int:pk>/',    views.promotion_update,  name='promotion_update'),
    path('delete/<int:pk>/',  views.promotion_delete,  name='promotion_delete'),
    path('validate/',         views.validate_promo,    name='validate_promo'),
]
