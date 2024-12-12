from django.test import TestCase
from TASchedulerApp.models import MyCourse, MyUser
from unittest.mock import Mock, patch
from django.contrib.auth import get_user_model
from TASchedulerApp.service.account_service import AccountService

class EditUserTests(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create_user(
            name='OldName',
            email='old@uwm.edu',
            role='Instructor',
            password='OldPassword'
        )

    def test_edit_user_name(self):
        new_data = {'new_name': 'Jeff'}
        AccountService.edit_user(self.user.id, new_data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Jeff')

    def test_edit_user_password(self):
        new_data = {'new_password': 'password123abc'}
        AccountService.edit_user(self.user.id, new_data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('password123abc'))

    def test_edit_user_contact_info(self):
        new_data = {'new_contact_info': 'jeff73@uwm.edu'}
        AccountService.edit_user(self.user.id, new_data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.contactInfo, 'jeff73@uwm.edu')

    def test_edit_user_role(self):
        new_data = {'new_role': 'TA'}
        AccountService.edit_user(self.user.id, new_data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'TA')

    def test_edit_multiple_fields(self):
        new_data = {
            'new_name': 'Benjamin',
            'new_password': 'monstertrucks19',
            'new_contact_info': 'bigben10@uwm.edu',
            'new_role': 'TA',
        }
        AccountService.edit_user(self.user.id, new_data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Benjamin')
        self.assertTrue(self.user.check_password('monstertrucks19'))
        self.assertEqual(self.user.contactInfo, 'bigben10@uwm.edu')
        self.assertEqual(self.user.role, 'TA')

    def test_edit_no_changes(self):
        old_data = {
            'old_name': self.user.name,
            'old_password': self.user.password,
            'old_email': self.user.email,
            'old_role': self.user.role,
        }
        AccountService.edit_user(self.user.id, old_data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, old_data['old_name'])
        self.assertEqual(self.user.password, old_data['old_password'])
        self.assertEqual(self.user.email, old_data['old_email'])
        self.assertEqual(self.user.role, old_data['old_role'])