from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # 1. Update the columns shown in the main list view
    list_display = ('username', 'email', 'role', 'course', 'year', 'is_approved', 'is_staff')
    
    # 2. Add helpful filters to the right sidebar
    list_filter = ('role', 'is_approved', 'course', 'year', 'is_staff')
    
    # 3. Add the fields to the "Edit User" screen
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Permissions', {
            'fields': ('role', 'is_approved')
        }),
        ('Academic Identity (Students Only)', {
            'fields': ('course', 'year', 'section'),
            'description': 'Leave these blank for Faculty and Admin accounts.'
        }),
    )
    
    # 4. Add the fields to the "Add User" screen (when creating a user manually from the admin)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Profile Details', {
            'classes': ('wide',),
            'fields': ('role', 'course', 'year', 'section', 'is_approved')
        }),
    )

# Register the custom model with the custom admin class
admin.site.register(CustomUser, CustomUserAdmin)