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
    home_address = models.TextField(default='')
    phone_number = models.CharField(max_length=15, default='')
    office_hours = models.TextField(default='')
    office_location = models.CharField(max_length=50, default='')
    skills = models.TextField(default='')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = MyUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True
        return False

    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True
        return False


class CustomUser(AbstractBaseUser):
    ROLE_CHOICES = [
        ('TA', 'Teaching Assistant'),
        ('Instructor', 'Instructor'),
        ('Admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='TA')


class MyCourse(models.Model):
    name = models.CharField(max_length=100)
    instructor = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'Instructor'},
        related_name='courses',
        null=True,
        blank=True
    )
    tas = models.ManyToManyField(
        MyUser,
        limit_choices_to={'role': 'TA'},
        related_name='ta_courses',
        blank=True
    )
    room = models.CharField(max_length=10)
    time = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Notification(models.Model):
    title = models.CharField(max_length=255)
    time_received = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(max_length=255)
    recipient = models.ForeignKey(MyUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class LabSection(models.Model):
    name = models.CharField(max_length=255)
    section = models.CharField(max_length=50)
    course = models.ForeignKey(
        MyCourse,
        on_delete=models.CASCADE,
        related_name='lab_sections'
    )
    instructor = models.ForeignKey(
        MyUser,
        on_delete=models.SET_NULL,
        limit_choices_to={'role': 'Instructor'},
        related_name='lab_sections',
        null=True,
        blank=True
    )
    ta = models.ForeignKey(
        MyUser,
        on_delete=models.SET_NULL,
        limit_choices_to={'role': 'TA'},
        related_name='lab_sections_ta',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name