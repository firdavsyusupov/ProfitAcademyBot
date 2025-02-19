from django.contrib import admin
from .models import User, Course, Promocode, Group, Payment, Channel, Admin


class UserAdminSite(admin.ModelAdmin):
    list_display = ('name', 'phone', 'city', 'username', 'userid', 'current_time')

class CourseAdminSite(admin.ModelAdmin):
    list_display = ('title', 'price', 'duration')

class PromocodeAdminSite(admin.ModelAdmin):
    list_display = ('course', 'code', 'discount_percentage', 'limit_count', 'start', 'end')

class GroupAdminSite(admin.ModelAdmin):
    list_display = ('title', 'chat_id')

class PaymentAdminSite(admin.ModelAdmin):
    list_display = ('user_id', 'course_id', 'promocode_id', 'payment', 'photo', 'time')

class ChannelAdminSite(admin.ModelAdmin):
    list_display = ('course_id', 'url')

class AdminAdminSite(admin.ModelAdmin):
    list_display = ('name', 'username')

admin.site.register(User, UserAdminSite)
admin.site.register(Course, CourseAdminSite)
admin.site.register(Promocode, PromocodeAdminSite)
admin.site.register(Group, GroupAdminSite)
admin.site.register(Payment, PaymentAdminSite)
admin.site.register(Channel, ChannelAdminSite)
admin.site.register(Admin, AdminAdminSite)
