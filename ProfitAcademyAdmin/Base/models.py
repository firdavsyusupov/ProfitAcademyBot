from urllib.parse import uses_query

from django.db import models
from django.db.models import ForeignKey

class User(models.Model):
    userid = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    username = models.CharField(max_length=50)
    current_time = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'users'
        managed = False
        verbose_name = 'user'
        verbose_name_plural = 'users'

class Course(models.Model):
    title = models.CharField(max_length=100, unique=True)
    photo = models.ImageField(upload_to="photos/course/")
    description = models.TextField()
    price = models.IntegerField()
    duration = models.IntegerField()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'courses'
        managed = False
        verbose_name = 'course'
        verbose_name_plural = 'courses'

class Promocode(models.Model):
    course = ForeignKey(Course, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.IntegerField()
    limit_count = models.IntegerField()
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return f"{self.code} for {self.course.title}"

    class Meta:
        db_table = 'promocodes'
        managed = False
        verbose_name = 'promocode'
        verbose_name_plural = 'promocodes'

class Group(models.Model):
    title = models.CharField(max_length=100, default="Admins' Group")
    chat_id = models.IntegerField()

    class Meta:
        db_table = 'groups'
        managed = False
        verbose_name = 'group'
        verbose_name_plural = 'groups'

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="photos/cheques/")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    payment = models.IntegerField()
    promocode = models.ForeignKey(Promocode, on_delete=models.CASCADE)
    comment = models.TextField(null=True)
    time = models.DateTimeField()

    class Meta:
        db_table = 'payments'
        managed = False
        verbose_name = 'payment'
        verbose_name_plural = 'payments'

class Channel(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    url = models.CharField(max_length=150)

    class Meta:
        db_table = 'channels'
        managed = False
        verbose_name = 'channel'
        verbose_name_plural = 'channels'

