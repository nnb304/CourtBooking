from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


# ĐĂNG KÝ USER VÀO ADMIN
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Thêm phone và role vào phần "Thông tin cá nhân"
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin bổ sung', {'fields': ('phone', 'role')}),
    )
