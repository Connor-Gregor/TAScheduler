from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class MyUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, name, password, **extra_fields)

class MyUser(AbstractBaseUser):
    ROLE_CHOICES = [
        ('Administrator', 'Administrator'),
        ('Instructor', 'Instructor'),
        ('TA', 'TA'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='TA')
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50, unique=True)
    contactInfo = models.CharField(max_length=50, default='')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = MyUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.name

class CustomUser(AbstractBaseUser):
    ROLE_CHOICES = [
        ('TA', 'Teaching Assistant'),
        ('Instructor', 'Instructor'),
        ('Admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='TA')
