from django.contrib import admin
from .models import Booking


# ĐĂNG KÝ ĐẶT SÂN VÀO TRANG ADMIN
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display  = ['court', 'user', 'date', 'start_time', 'duration_hours',
                      'promotion', 'discount_amount', 'total_price', 'status']
    list_filter   = ['status', 'date']
    search_fields = ['court__name', 'user__email']
