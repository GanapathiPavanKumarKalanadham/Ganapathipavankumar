from django.db import models

class CardDetail(models.Model):
    CARD_TYPE_CHOICES = [
        ('PAN', 'PAN'),
        ('Aadhaar', 'Aadhaar'),
    ]
    type = models.CharField(max_length=10, choices=CARD_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=20, blank=True, null=True)
    dob = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    aadhar_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.type} - {self.name}"


class UserProfile(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
