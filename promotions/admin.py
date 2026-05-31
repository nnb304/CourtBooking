from django.contrib import admin

from .models import Promotion


# ĐĂNG KÝ MÃ KHUYẾN MẠI VÀO TRANG ADMIN
@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display  = ['code', 'discount_type', 'discount_value', 'start_date', 'end_date', 'is_active']
    list_filter   = ['discount_type', 'is_active']
    search_fields = ['code', 'description']
