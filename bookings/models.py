from datetime import datetime, timedelta
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


# MODEL ĐẶT SÂN
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Chờ duyệt'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã huỷ'),
    ]

    court          = models.ForeignKey(
        'courts.Court',
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Sân'
    )
    user           = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Người đặt'
    )
    date           = models.DateField(verbose_name='Ngày chơi')
    start_time     = models.TimeField(verbose_name='Giờ bắt đầu')
    duration_hours = models.PositiveSmallIntegerField(
        verbose_name='Số giờ',
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    promo_code      = models.ForeignKey(
        'promotions.PromoCode',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Mã khuyến mãi'
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=0,
        default=0,
        verbose_name='Số tiền giảm'
    )
    total_price    = models.DecimalField(
        max_digits=10, decimal_places=0,
        verbose_name='Tổng tiền (VNĐ)'
    )
    status         = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Trạng thái'
    )
    created_at     = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Đặt sân'
        verbose_name_plural = 'Danh sách đặt sân'

    def __str__(self):
        return f"{self.court.name} | {self.date} | {self.start_time.strftime('%H:%M')}"

    @property
    def end_time(self):
        """Tính giờ kết thúc dựa trên giờ bắt đầu + số giờ thuê."""
        dt = datetime.combine(datetime.today(), self.start_time)
        return (dt + timedelta(hours=self.duration_hours)).time()
