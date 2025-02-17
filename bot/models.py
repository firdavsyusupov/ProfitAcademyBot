from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Менеджер пользователя
class UserManager(BaseUserManager):
    def create_user(self, telegram_id, name, phone, city, **extra_fields):
        if not telegram_id:
            raise ValueError('The Telegram ID is required')
        user = self.model(telegram_id=telegram_id, name=name, phone=phone, city=city, **extra_fields)
        user.save(using=self._db)
        return user

# Модель пользователя
class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    telegram_nickname = models.CharField(max_length=255, blank=True, null=True)
    telegram_username = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)  # <-- Это поле есть
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Модель курса
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='courses/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Модель промокода
class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    usage_limit = models.PositiveIntegerField()
    used_count = models.PositiveIntegerField(default=0)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def use(self):
        if self.used_count < self.usage_limit and self.is_active:
            self.used_count += 1
            self.save()
            return True
        return False
