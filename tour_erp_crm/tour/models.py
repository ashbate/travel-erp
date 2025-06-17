from django.db import models
from django.conf import settings

class Tour(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    TRAVEL_MODE_CHOICES = [
        ('bus', 'Bus'),
        ('plane', 'Plane'),
        ('train', 'Train'),
        ('mixed', 'Mixed'),
        # Consider adding 'ship', 'car', etc. if needed
    ]

    name = models.CharField(max_length=200)
    destinations = models.TextField(help_text="List of destinations, comma-separated or one per line.")
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='planned')
    travel_mode = models.CharField(max_length=10, choices=TRAVEL_MODE_CHOICES, blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # Or models.SET_NULL if tours should remain if user is deleted
        related_name='tours_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"

    class Meta:
        ordering = ['-start_date', 'name']
        verbose_name = "Tour"
        verbose_name_plural = "Tours"

    travelers = models.ManyToManyField('traveler.Traveler', through='TourBooking', related_name='booked_tours')

    # Basic validation example (can be expanded)
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")
        super().clean()

    # Example property
    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return None

class TourBooking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending_payment', 'Pending Payment'),
        ('cancelled', 'Cancelled'),
        ('waitlisted', 'Waitlisted'),
    ]

    tour = models.ForeignKey('Tour', on_delete=models.CASCADE, related_name='bookings')
    traveler = models.ForeignKey('traveler.Traveler', on_delete=models.CASCADE, related_name='tour_bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending_payment')
    notes = models.TextField(blank=True, null=True)
    room_configuration = models.TextField(blank=True, null=True, help_text="e.g., Single Room, Double shared with Jane Doe")

    def __str__(self):
        return f"Booking for {self.traveler} on {self.tour.name} ({self.status})"

    class Meta:
        ordering = ['-booking_date']
        unique_together = ('tour', 'traveler') # A traveler can only be booked once on the same tour
        verbose_name = "Tour Booking"
        verbose_name_plural = "Tour Bookings"
