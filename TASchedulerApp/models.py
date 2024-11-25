# Create your models here.
from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('Administrator', 'Administrator'),
        ('Instructor', 'Instructor'),
        ('TA', 'TA'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='TA')
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    contactInfo = models.CharField(max_length=50)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'name'
    PASSWORD_FIELD = 'password'
    CONTACT_FIELD = 'contactInfo'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=50, unique=True)
    id = models.IntegerField(unique=True)
    semester = models.CharField(max_length=50)
    instructor = models.CharField(max_length=50)
    ta = models.ManyToManyField(User)
    students = models.ManyToManyField(User)
    lab_sections = models.CharField(max_length=50)

    def __str__(self):
        return " ".join([self.name, self.id, self.semester])

class LabSection(models.Model):
    name = models.CharField(max_length=50, unique=True)
    id = models.IntegerField(unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.CharField(max_length=50)
    instructor = models.CharField(max_length=50)
    ta = models.ManyToManyField(User)
    students = models.ManyToManyField(User)

    def __str__(self):
        return " ".join([self.name, self.id, self.semester])