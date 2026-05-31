from django.db import models


class Payment(models.Model):

    METHOD_CHOICES = [
        ('cash',    'Tiền mặt'),
        ('momo',    'MoMo'),
        ('banking', 'Chuyển khoản'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('success', 'Thành công'),
        ('failed',  'Thất bại'),
    ]

    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='payment',
    )
    method  = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status  = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Thanh toán #{self.pk} — {self.booking} [{self.get_status_display()}]'
