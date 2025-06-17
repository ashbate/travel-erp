from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tour_booking_id', # Displaying ID for brevity, can link to tour_booking object too
        'amount',
        'payment_date',
        'payment_method',
        'status',
        'transaction_id',
        'recorded_by',
    )
    list_filter = (
        'status',
        'payment_method',
        'payment_date',
        'recorded_by',
        'tour_booking__tour__name', # Filter by tour name via tour_booking
    )
    search_fields = (
        'transaction_id',
        'notes',
        'tour_booking__traveler__first_name', # Search by traveler's name
        'tour_booking__traveler__last_name',
        'tour_booking__traveler__email',
        'tour_booking__tour__name', # Search by tour name
    )
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['tour_booking', 'recorded_by']

    fieldsets = (
        (None, {
            'fields': ('tour_booking', 'amount', 'payment_date', 'payment_method', 'status')
        }),
        ('Details', {
            'fields': ('transaction_id', 'notes')
        }),
        ('Audit', {
            'fields': ('recorded_by', 'created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.recorded_by_id: # If 'recorded_by' is not already set
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)

    # Consider adding a reference to the tour and traveler in list_display for clarity
    def get_tour_name(self, obj):
        return obj.tour_booking.tour.name
    get_tour_name.short_description = 'Tour'
    get_tour_name.admin_order_field = 'tour_booking__tour__name'

    def get_traveler_name(self, obj):
        return obj.tour_booking.traveler
    get_traveler_name.short_description = 'Traveler'
    get_traveler_name.admin_order_field = 'tour_booking__traveler'

    # Add to list_display if desired
    # list_display = ('id', 'get_tour_name', 'get_traveler_name', 'amount', ...)
    # Be mindful of performance if these lookups become too expensive for large lists.
    # Using tour_booking_id directly as in the original list_display is often more performant.
