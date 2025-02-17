from django.contrib import admin
from .models import User, Course, Promocode, Group, Payment


class UserAdminSite(admin.ModelAdmin):
    list_display = ('name', 'phone', 'city', 'username', 'userid', 'current_time')

class CourseAdminSite(admin.ModelAdmin):
    list_display = ('title', 'price', 'duration')

class PromocodeAdminSite(admin.ModelAdmin):
    list_display = ('course', 'code', 'discount_percentage', 'limit_count', 'start', 'end')

class GroupAdminSite(admin.ModelAdmin):
    list_display = ('title', 'chat_id')

class PaymentAdminSite(admin.ModelAdmin):
    list_display = ('user', 'course', 'promocode', 'time')

admin.site.register(User, UserAdminSite)
admin.site.register(Course, CourseAdminSite)
admin.site.register(Promocode, PromocodeAdminSite)
admin.site.register(Group, GroupAdminSite)
admin.site.register(Payment, PaymentAdminSite)