from django.contrib import admin
from .models import Traveler

@admin.register(Traveler)
class TravelerAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'first_name',
        'last_name',
        'phone_number',
        'passport_number',
        'user', # The tour operator who added this traveler
        'date_added',
        'last_updated',
    )
    search_fields = (
        'first_name',
        'last_name',
        'email',
        'passport_number',
        'user__username', # Search by the username of the managing user
    )
    list_filter = (
        'passport_issuing_country',
        'date_added',
        'last_updated',
        'user',
    )
    readonly_fields = ('date_added', 'last_updated')
    fieldsets = (
        (None, {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Passport Information', {
            'fields': ('passport_number', 'passport_expiry_date', 'passport_issuing_country'),
            'classes': ('collapse',), # Collapsible section
        }),
        ('Visa Information', {
            'fields': ('visa_info',),
            'classes': ('collapse',),
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('date_added', 'last_updated'),
        }),
    )

    # If you want to automatically set the 'user' field to the currently logged-in user
    # when adding a traveler in the admin, you can override save_model:
    def save_model(self, request, obj, form, change):
        if not obj.pk: # If creating a new object
            obj.user = request.user
        super().save_model(request, obj, form, change)
