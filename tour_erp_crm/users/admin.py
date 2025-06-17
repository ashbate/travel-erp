from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Add 'role' to the display and list_filter
    list_display = BaseUserAdmin.list_display + ('role',)
    list_filter = BaseUserAdmin.list_filter + ('role',)

    # Add 'role' to fieldsets for editing in the admin
    # This requires careful integration with existing BaseUserAdmin fieldsets
    # For simplicity, let's add a new section for 'role'
    # Or, if you want to modify existing sections, you'll need to copy and extend them

    # Add 'role' to the Add User form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

    # Add 'role' to the Change User form
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )

    # Ensure search_fields includes fields you want to search by for autocomplete
    search_fields = BaseUserAdmin.search_fields + ('email', 'first_name', 'last_name') # 'username' is already in BaseUserAdmin.search_fields
