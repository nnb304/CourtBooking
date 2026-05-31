from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ('pk', 'booking', 'method', 'status', 'paid_at')
    list_filter   = ('status', 'method')
    search_fields = ('booking__court__name', 'booking__user__username')
    readonly_fields = ('paid_at',)
