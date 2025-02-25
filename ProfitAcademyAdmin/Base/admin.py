from django.contrib import admin
from .models import User, Course, Promocode, Group, Payment, Channel

class UserAdminSite(admin.ModelAdmin):
    list_display = ('name', 'phone', 'city', 'username', 'userid', 'current_time')

class CourseAdminSite(admin.ModelAdmin):
    list_display = ('title', 'price', 'duration')

class PromocodeAdminSite(admin.ModelAdmin):
    list_display = ('course', 'code', 'discount_percentage', 'limit_count', 'start', 'end')

class GroupAdminSite(admin.ModelAdmin):
    list_display = ('title', 'chat_id')

class PaymentAdminSite(admin.ModelAdmin):
    list_display = ('name', 'course_title', 'promo_code', 'payment', 'photo', 'time')

    def name(self, obj):
        return obj.user.name

    def course_title(self, obj):
        return obj.course.title

    def promo_code(self, obj):
        return obj.promocode.code

class ChannelAdminSite(admin.ModelAdmin):
    list_display = ('course', 'url')


admin.site.register(User, UserAdminSite)
admin.site.register(Course, CourseAdminSite)
admin.site.register(Promocode, PromocodeAdminSite)
admin.site.register(Group, GroupAdminSite)
admin.site.register(Payment, PaymentAdminSite)
admin.site.register(Channel, ChannelAdminSite)
