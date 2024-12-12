from django.test import TestCase
from django.core.exceptions import ValidationError
from TASchedulerApp.models import MyUser
from TASchedulerApp.service.account_service import AccountService

class AccountServiceTests(TestCase):

    def test_create_account_valid_input(self):
        name = "John Doe"
        email = "john.doe@example.com"
        role = "Instructor"
        password = "SecureP@ssw0rd"

        user = AccountService.create_account(name, email, role, password)

        self.assertIsInstance(user, MyUser)
        self.assertEqual(user.name, name)
        self.assertEqual(user.email, email)
        self.assertEqual(user.role, role)
        self.assertTrue(user.check_password(password))
