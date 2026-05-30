from django.contrib import admin
from .models import Review


# ĐĂNG KÝ ĐÁNH GIÁ VÀO TRANG ADMIN
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ['court', 'user', 'rating', 'created_at']
    list_filter   = ['rating', 'created_at']
    search_fields = ['court__name', 'user__email']
