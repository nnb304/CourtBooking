from datetime import datetime, timedelta

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction


# GIỜ MỞ CỬA / ĐÓNG CỬA VÀ THỜI GIAN GIỮ CHỖ CHỜ THANH TOÁN
OPEN_HOUR      = 6     # 06:00
CLOSE_HOUR     = 22    # 22:00 (giờ kết thúc muộn nhất)
SLOT_MINUTES   = 30    # mỗi slot 30 phút
TOTAL_SLOTS    = (CLOSE_HOUR - OPEN_HOUR) * 60 // SLOT_MINUTES   # 32 slot
HOLD_MINUTES   = 15    # đơn chờ thanh toán quá 15 phút sẽ tự huỷ, nhả khung giờ


def time_to_slot(t):
    """Chuyển time → slot index (slot 0 = 06:00)."""
    return ((t.hour - OPEN_HOUR) * 60 + t.minute) // SLOT_MINUTES


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
    promotion       = models.ForeignKey(
        'promotions.Promotion',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Mã khuyến mãi'
    )
    # GIÁ GỐC = giá/giờ tại thời điểm đặt × số giờ.
    # Lưu cố định để đối chiếu (thuế, doanh thu) kể cả khi chủ sân đổi giá sau này.
    original_price  = models.DecimalField(
        max_digits=10, decimal_places=0,
        default=0,
        verbose_name='Giá gốc (VNĐ)'
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=0,
        default=0,
        verbose_name='Số tiền giảm'
    )
    total_price    = models.DecimalField(
        max_digits=10, decimal_places=0,
        verbose_name='Thực thu (VNĐ)'
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

    def slot_indices(self):
        """Các slot 30 phút mà đơn này chiếm."""
        start = time_to_slot(self.start_time)
        return range(start, start + self.duration_hours * 60 // SLOT_MINUTES)

    @property
    def hold_expires_at(self):
        return self.created_at + timedelta(minutes=HOLD_MINUTES)

    @property
    def is_hold_expired(self):
        return self.status == 'pending' and datetime.now() > self.hold_expires_at

    # GIỮ CHỖ: tạo các BookingSlot. Ràng buộc UNIQUE ở DB chặn mọi đơn chồng giờ (Lớp 2)
    def reserve_slots(self):
        BookingSlot.objects.bulk_create([
            BookingSlot(booking=self, court=self.court, date=self.date, slot=i)
            for i in self.slot_indices()
        ])

    # HUỶ ĐƠN: đổi trạng thái + nhả các slot để người khác đặt lại được
    def cancel(self):
        with transaction.atomic():
            self.status = 'cancelled'
            self.save(update_fields=['status'])
            self.slots.all().delete()


# MỖI DÒNG = 1 SLOT 30 PHÚT ĐANG BỊ CHIẾM CỦA 1 SÂN TRONG 1 NGÀY
class BookingSlot(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='slots')
    court   = models.ForeignKey('courts.Court', on_delete=models.CASCADE, related_name='booked_slots')
    date    = models.DateField()
    slot    = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['court', 'date', 'slot'], name='unique_court_date_slot'),
        ]
        verbose_name = 'Slot đã đặt'
        verbose_name_plural = 'Slot đã đặt'

    def __str__(self):
        return f"{self.court_id} | {self.date} | slot {self.slot}"


def expire_stale_pending(court=None):
    """Huỷ các đơn chờ thanh toán quá HOLD_MINUTES để nhả khung giờ."""
    cutoff = datetime.now() - timedelta(minutes=HOLD_MINUTES)
    stale = Booking.objects.filter(status='pending', created_at__lt=cutoff)
    if court is not None:
        stale = stale.filter(court=court)
    for booking in stale:
        booking.cancel()
