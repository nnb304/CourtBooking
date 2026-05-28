from django.contrib import admin
from .models import Court, Favorite


# ĐĂNG KÝ SÂN VÀO TRANG ADMIN
@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display  = ['name', 'court_type', 'district', 'price_per_hour', 'is_active', 'owner']
    list_filter   = ['court_type', 'district', 'is_active']
    search_fields = ['name', 'address']


# ĐĂNG KÝ SÂN YÊU THÍCH VÀO TRANG ADMIN
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'court', 'created_at']
