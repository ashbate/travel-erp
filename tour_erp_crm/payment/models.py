from django.db import models
from django.conf import settings
# Ensure tour.TourBooking can be referenced. It's good practice to import explicitly if needed,
# but string references like 'tour.TourBooking' in ForeignKey are often fine.

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('paypal', 'PayPal'),
        ('other', 'Other'),
    ]

    tour_booking = models.ForeignKey(
        'tour.TourBooking',
        on_delete=models.CASCADE, # If booking is deleted, payments are deleted.
                                  # Consider models.SET_NULL or PROTECT if payments need to be archived.
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # If user who recorded payment is deleted, payment record remains.
        null=True,
        blank=True, # Can be system-recorded or by an optional user.
        related_name='recorded_payments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment of {self.amount} for booking {self.tour_booking_id} ({self.status})"

    class Meta:
        ordering = ['-payment_date', '-created_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
