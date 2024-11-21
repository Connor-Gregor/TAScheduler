from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from TASchedulerApp.services import AccountService
import unittest
from unittest.mock import Mock

# Create your tests here.

class TestCreateAccount(unittest.TestCase):
    def setUp(self):
        self.user_in_db = {
            'email': 'john@uwm.edu',
            'name': 'John Burgerton',
            'password': '123abc',
            'contactInfo': '(414)123-4567'
        }
        User.objects.create(
            email=self.user_in_db['email'],
            name=self.user_in_db['name'],
            password=self.user_in_db['password'],
            contactInfo=self.user_in_db['contactInfo']
        )

    def test_nonuniqueEmail(self):
        # email is unique
        with self.assertRaises(IntegrityError, msg="email already exists and exception wasn't raised"):
            acc = AccountService()
            acc.createAccount("john@uwm.edu", "Johnathan Hamburger", "456def", "(414)987-6543")

    def test_invalidEmailFormat(self):
        # email follows the proper format
        with self.assertRaises(ValueError, msg="email doesn't follow proper format and exception wasn't raised"):
            acc = AccountService()
            acc.createAccount("johnuwm.edu", "John Burgerton", "123abc", "(414)123-4567")

    def test_invalidArg(self):
        # name, password, and contactInfo are non-null strings
        with self.assertRaises(TypeError, msg="non-string argument passed into constructor and exception wasn't raised"):
            acc = AccountService()
            acc.createAccount(123, ['a'], {2,3}, 1234567890)

    def test_accountCreated(self):
        acc = AccountService()
        acc.createAccount("bobathan7@uwm.edu", "Jim Bob", "boblyfe12", "(312)523-1847")
        self.assertNotEqual(acc, None, msg="Account was not created")

    def test_accountInDatabase(self):
        acc = AccountService()
        acc.createAccount("bobathan7@uwm.edu", "Jim Bob", "boblyfe12", "(312)523-1847")
        self.assertEqual(User.objects.filter(email = "bobathan7@uwm.edu").exists(), True, msg="Account was not saved in the database")