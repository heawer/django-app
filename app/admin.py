from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subject, Enrollment

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'role', 'email', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Subject)
admin.site.register(Enrollment)
