from django.db import models
from django.conf import settings


# MODEL SÂN THỂ THAO
class Court(models.Model):
    COURT_TYPE_CHOICES = [
        ('badminton',  'Cầu lông'),
        ('football',   'Bóng đá'),
        ('pickleball', 'Pickleball'),
        ('basketball', 'Bóng rổ'),
        ('tennis',     'Tennis'),
    ]

    DISTRICT_CHOICES = [
        ('cau_giay',     'Cầu Giấy'),
        ('dong_da',      'Đống Đa'),
        ('hai_ba_trung', 'Hai Bà Trưng'),
        ('hoan_kiem',    'Hoàn Kiếm'),
        ('thanh_xuan',   'Thanh Xuân'),
        ('ha_dong',      'Hà Đông'),
        ('bac_tu_liem',  'Bắc Từ Liêm'),
        ('nam_tu_liem',  'Nam Từ Liêm'),
        ('khac',         'Khác'),
    ]

    name           = models.CharField(max_length=200, verbose_name='Tên sân')
    court_type     = models.CharField(max_length=20, choices=COURT_TYPE_CHOICES, verbose_name='Loại sân')
    address        = models.CharField(max_length=300, verbose_name='Địa chỉ')
    district       = models.CharField(max_length=20, choices=DISTRICT_CHOICES, default='khac',
                                      blank=True, verbose_name='Quận/Huyện')
    description    = models.TextField(blank=True, verbose_name='Mô tả')
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Giá thuê/giờ (VNĐ)')
    image          = models.ImageField(upload_to='courts/', blank=True, null=True, verbose_name='Ảnh sân')
    is_active      = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    owner          = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courts',
        verbose_name='Chủ sân'
    )
    created_at     = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sân'
        verbose_name_plural = 'Danh sách sân'

    def __str__(self):
        return self.name


# MODEL SÂN YÊU THÍCH
class Favorite(models.Model):
    user  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    court = models.ForeignKey(
        Court,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'court')  # mỗi user chỉ thích 1 sân 1 lần
        verbose_name = 'Sân yêu thích'
        verbose_name_plural = 'Sân yêu thích'

    def __str__(self):
        return f"{self.user.username} - {self.court.name}"
