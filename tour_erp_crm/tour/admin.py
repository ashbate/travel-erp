from django.contrib import admin
from .models import Tour, TourBooking
from payment.models import Payment # Import Payment model

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    fields = ('amount', 'payment_date', 'payment_method', 'status', 'transaction_id', 'notes')
    readonly_fields = ('recorded_by',) # 'recorded_by' will be set automatically or can be omitted if always current user

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # This can be used to limit choices or set initial values if needed
        # For example, if 'recorded_by' should default to current user but still be editable by some.
        # if db_field.name == "recorded_by":
        #     kwargs["initial"] = request.user.id
        #     # kwargs["queryset"] = User.objects.filter(is_staff=True) # Example filter
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # This method is not called for inlines. save_formset is used.
        # To set 'recorded_by' automatically for new payments in inline:
        # We need to override save_formset in TourBookingAdmin.
        pass


class TourBookingInline(admin.TabularInline): # Or admin.StackedInline for a different layout
    model = TourBooking
    extra = 1 # Number of empty forms to display
    autocomplete_fields = ['traveler'] # If you have many travelers, for better UX

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'start_date',
        'end_date',
        'status',
        'travel_mode',
        'created_by',
        'duration_days', # Display the custom property
    )
    search_fields = (
        'name',
        'destinations',
        'created_by__username',
    )
    list_filter = (
        'status',
        'travel_mode',
        'start_date',
        'end_date',
        'created_by',
    )
    readonly_fields = ('created_at', 'updated_at', 'duration_days')
    fieldsets = (
        (None, {
            'fields': ('name', 'destinations', 'description')
        }),
        ('Schedule & Status', {
            'fields': ('start_date', 'end_date', 'status', 'travel_mode')
        }),
        ('Management', {
            'fields': ('created_by',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk: # If creating a new tour
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # Optional: Add a custom action
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Mark selected tours as completed"

    actions = [mark_as_completed]
    inlines = [TourBookingInline]

@admin.register(TourBooking)
class TourBookingAdmin(admin.ModelAdmin):
    list_display = ('tour', 'traveler', 'status', 'booking_date', 'room_configuration')
    list_filter = ('status', 'booking_date', 'tour__name') # Filter by tour name
    inlines = [PaymentInline] # Add PaymentInline here
    search_fields = ('tour__name', 'traveler__first_name', 'traveler__last_name', 'traveler__email', 'notes')
    autocomplete_fields = ['tour', 'traveler'] # Essential for good UX with ForeignKey fields
    readonly_fields = ('booking_date',)
    fieldsets = (
        (None, {
            'fields': ('tour', 'traveler', 'status')
        }),
        ('Details', {
            'fields': ('room_configuration', 'notes', 'booking_date')
        }),
    )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Payment) and not instance.pk and not instance.recorded_by_id:
                # If it's a new Payment object and recorded_by is not set
                instance.recorded_by = request.user
            instance.save()
        formset.save_m2m()
        super().save_formset(request, form, formset, change)
