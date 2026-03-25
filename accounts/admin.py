from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import Profile,User

admin.site.unregister(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id","username", "email", "is_staff", "is_active")
# @admin.register(User,CustomUserAdmin)

admin.site.register(User,CustomUserAdmin)


@admin.register(Profile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("Role", "Name", "Designation","Employee_id")

