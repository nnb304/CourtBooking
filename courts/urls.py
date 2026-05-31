from django.urls import path
from . import views

app_name = 'courts'

urlpatterns = [
    # TRANG CÔNG KHAI
    path('', views.court_list, name='court_list'),
    path('court/<int:pk>/', views.court_detail, name='court_detail'),
    path('court/<int:pk>/favorite/', views.toggle_favorite_view, name='toggle_favorite'),
    path('favorites/', views.favorite_list_view, name='favorite_list'),
    # QUẢN LÝ SÂN (owner)
    path('my/', views.my_court_list, name='my_court_list'),
    path('add/', views.court_create, name='court_create'),
    path('edit/<int:pk>/', views.court_update, name='court_update'),
    path('delete/<int:pk>/', views.court_delete, name='court_delete'),
    # DUYỆT SÂN (admin)
    path('pending/', views.court_pending_list, name='court_pending_list'),
    path('approve/<int:pk>/', views.court_approve, name='court_approve'),
    path('reject/<int:pk>/', views.court_reject, name='court_reject'),
]
