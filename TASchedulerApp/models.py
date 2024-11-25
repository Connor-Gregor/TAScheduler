from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class MyUser(AbstractUser):
    ROLE_CHOICES = [
        ('Administrator', 'Administrator'),
        ('Instructor', 'Instructor'),
        ('TA', 'TA'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='TA')
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150, unique=True)

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.name