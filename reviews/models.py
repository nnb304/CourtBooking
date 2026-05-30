from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# MODEL ĐÁNH GIÁ SÂN
class Review(models.Model):
    court = models.ForeignKey(
        'courts.Court',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Sân'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Người đánh giá'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Điểm đánh giá (1–5)'
    )
    comment = models.TextField(max_length=500, verbose_name='Nhận xét')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày đánh giá')

    class Meta:
        ordering = ['-created_at']
        unique_together = ('court', 'user')
        verbose_name = 'Đánh giá'
        verbose_name_plural = 'Danh sách đánh giá'

    def __str__(self):
        return f"{self.user.email} - {self.court.name} - {self.rating}★"
