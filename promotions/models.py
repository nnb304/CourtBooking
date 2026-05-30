from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models


# MODEL MÃ KHUYẾN MẠI
class PromoCode(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Giảm theo %'),
        ('flat',    'Giảm số tiền cố định (VND)'),
    ]

    code           = models.CharField(max_length=20, unique=True, verbose_name='Mã khuyến mãi')
    description    = models.CharField(max_length=200, blank=True, verbose_name='Mô tả')
    discount_type  = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES,
                                      verbose_name='Loại giảm giá')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2,
                                         verbose_name='Giá trị giảm')
    start_date     = models.DateTimeField(verbose_name='Ngày bắt đầu')
    end_date       = models.DateTimeField(verbose_name='Ngày kết thúc')
    is_active      = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    created_at     = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mã khuyến mãi'
        verbose_name_plural = 'Danh sách mã khuyến mãi'

    # VALIDATE GIÁ TRỊ GIẢM VÀ KHOẢNG THỜI GIAN
    def clean(self):
        if self.discount_value is not None:
            if self.discount_type == 'percent' and not (0 <= self.discount_value <= 100):
                raise ValidationError({'discount_value': 'Giảm theo % phải nằm trong khoảng 0–100.'})
            if self.discount_type == 'flat' and self.discount_value <= 0:
                raise ValidationError({'discount_value': 'Giảm số tiền phải lớn hơn 0.'})

        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError({'end_date': 'Ngày kết thúc phải sau ngày bắt đầu.'})

    # KIỂM TRA MÃ CÒN HIỆU LỰC TẠI THỜI ĐIỂM HIỆN TẠI
    def is_valid_now(self):
        now = datetime.now()
        return bool(self.is_active and self.start_date <= now <= self.end_date)

    def __str__(self):
        if self.discount_type == 'percent':
            val = f"{self.discount_value:g}"
            return f"{self.code} (-{val}%)"
        else:
            val = int(self.discount_value)
            formatted = f"{val:,}".replace(',', '.')
            return f"{self.code} (-{ formatted}đ)"
