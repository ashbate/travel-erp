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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.role:
            from django.contrib.auth.models import Group
            try:
                group = Group.objects.get(name=self.role)
                self.groups.set([group])
            except Group.DoesNotExist:
                # Handle case where group might not exist, though our migration should create them
                pass
