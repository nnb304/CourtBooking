from django.contrib import admin

from .models import PromoCode


# ĐĂNG KÝ MÃ KHUYẾN MẠI VÀO TRANG ADMIN
@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display  = ['code', 'discount_type', 'discount_value', 'start_date', 'end_date', 'is_active']
    list_filter   = ['discount_type', 'is_active']
    search_fields = ['code', 'description']
