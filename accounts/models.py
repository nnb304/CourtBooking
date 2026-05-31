from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('guest',  'Khách'),
        ('player', 'Người chơi'),
        ('owner',  'Chủ sân'),
        ('admin',  'Quản trị'),
    ]
    phone = models.CharField(max_length=15, blank=True)
    role  = models.CharField(max_length=10, choices=ROLE_CHOICES, default='player')

    def __str__(self):
        return self.username
