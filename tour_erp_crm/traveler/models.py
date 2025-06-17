from django.db import models
from django.conf import settings # To get the AUTH_USER_MODEL

class Traveler(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # If the user is deleted, their traveler profiles are also deleted.
                                 # Consider models.SET_NULL or models.PROTECT depending on requirements.
        related_name='travelers_managed'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    passport_number = models.CharField(max_length=50, blank=True, null=True)
    passport_expiry_date = models.DateField(blank=True, null=True)
    passport_issuing_country = models.CharField(max_length=100, blank=True, null=True)
    visa_info = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    class Meta:
        ordering = ['-date_added']
        verbose_name = "Traveler"
        verbose_name_plural = "Travelers"

    tours = models.ManyToManyField('tour.Tour', through='tour.TourBooking', related_name='booked_travelers')
