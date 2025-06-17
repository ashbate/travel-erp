from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('tour_operator', 'Tour Operator'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tour_operator')

    def __str__(self):
        return self.username
