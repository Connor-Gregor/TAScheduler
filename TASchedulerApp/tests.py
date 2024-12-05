from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase, Client
from django.urls import reverse

from TASchedulerApp.forms import CourseForm
from TASchedulerApp.models import MyCourse, MyUser, Notification
from TASchedulerApp.services import AccountService
import unittest
from unittest.mock import Mock, patch
from argparse import ArgumentTypeError
from TASchedulerApp.utils.Notification import notification
from django.contrib.auth import get_user_model
from TASchedulerApp.service.auth_service import AuthService
from TASchedulerApp.service.notification_service import NotificationService
from TASchedulerApp.service.account_service import AccountService
from TASchedulerApp.service.course_service import CourseService, assign_instructor_and_tas
#unused imports for now
#from TASchedulerApp.service.ta_assignment_service import TAAssignmentService
#from TASchedulerApp.service.contact_info_service import ContactInfoService


# Create your tests here.

class TestRedirectToDashboard(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create(
            name='user', password='password', role='Admin', email='admin@gmail.com'
        )

    def test_loginDisplay(self):
        # Simply test that the login actually displays
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    @patch('django.contrib.auth.authenticate')
    def test_login(self, mock_authenticate):
        # Test that login redirects to dashboard
        mock_user = Mock()
        mock_authenticate.return_value = mock_user

        response = self.client.post('/', {
            'username': self.user.name,
            'password': self.user.password
        })

        self.assertEqual(response.status_code, 200)

    def test_bad_login_username(self):
        # Test that an error message is shown for invalid username
        response = self.client.post('/', {
            'username': 'wrong_username',
            'password': self.user.password
        })
        self.assertContains(response, "Invalid username or password")

    def test_bad_login_password(self):
        # Test that an error message is shown for incorrect password
        response = self.client.post('/', {
            'username': self.user.name,
            'password': 'wrong_password'
        })
        self.assertContains(response, "Invalid username or password")

class TestCreateAccount(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create(
            email='john@uwm.edu',
            name='John Burgerton',
            password='123abc',
            contactInfo='(414)123-4567'
        )

    def test_non_uniqueEmail(self):
        # email is unique
        with self.assertRaises(IntegrityError):
            AccountService.create_account(
                name="Johnathan Hamburger",
                email="john@uwm.edu",  # Same email as in setUp
                role="Instructor",
                password="456def"
            )

    def test_accountCreated(self):
        acc = AccountService.create_account(
            name="Jim Bob",
            email="bobathan7@uwm.edu",
            role="TA",
            password="boblyfe12",
        )
        self.assertIsNotNone(acc, msg="Account was not created")

    def test_accountInDatabase(self):
        AccountService.create_account(
            name="Jim Bob",
            email="bobathan7@uwm.edu",
            role="TA",
            password="boblyfe12",
        )
        user_exists = MyUser.objects.filter(email="bobathan7@uwm.edu").exists()
        self.assertTrue(user_exists, msg="Account was not saved in the database")

    def test_password_hashing(self):
        password = "securepassword123"
        user = AccountService.create_account(
            name="Alice Example",
            email="alice@example.com",
            role="TA",
            password=password,
        )
        self.assertNotEqual(user.password, password, msg="Password was stored in plain text")
        self.assertTrue(user.check_password(password), msg="Password hash check failed")

    def test_role_assignment(self):
        user = AccountService.create_account(
            name="Bob Example",
            email="bob@example.com",
            role="Instructor",
            password="password123",
        )
        self.assertEqual(user.role, "Instructor", msg="Role assignment failed")


class TestAssignUsers(TestCase):
    def setUp(self):
        self.course = MyCourse.objects.create(
            id=1, name="Course 1", room="Room A", time="10:00 AM"
        )
        self.instructor = MyUser.objects.create(
            email="instructor1@example.com", name="Instructor 1", password="password", role="Instructor"
        )
        self.ta = MyUser.objects.create(
            email="ta1@example.com", name="TA 1", password="password", role="TA"
        )
        self.admin_user = MyUser.objects.create(
            email="admin@example.com", name="Admin User", password="password", role="Administrator"
        )
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_assign_users_get(self):
        response = self.client.get(reverse('assign_users_to_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Course 1")

    def test_assign_users_success(self):
        response = self.client.post(reverse('assign_users_to_course', args=[self.course.id]), {
            'instructor': self.instructor.id,
            'tas': self.ta.id
        })
        self.assertEqual(response.status_code, 302)

    def test_assign_users_no_ta(self):
        response = self.client.post(reverse('assign_users_to_course', args=[self.course.id]), {
            'instructor': self.instructor.id,
            'tas': ""
        })
        self.assertEqual(response.status_code, 302)

    def test_assign_users_no_instructor(self):
        response = self.client.post(reverse('assign_users_to_course', args=[self.course.id]), {
            'instructor': "",
            'tas': self.ta.id
        })
        self.assertEqual(response.status_code, 302)


class TestNotification(TestCase):
    def setUp(self):
        # Set up a test user
        self.user = MyUser.objects.create_user(
            email='testuser@example.com',
            password='password123',
            name='Test User'
        )
        self.sender = 'sender@example.com'

    def test_valid_email(self):
        recipient_email = 'testuser@example.com'
        message = "Test notification"

        result = NotificationService.send_notification(self.sender, recipient_email, message)

        self.assertTrue(result)
        notifications = NotificationService.get_user_notifications(self.user)

    def test_send_invalid_recipient(self):
        invalid_email = 'invalid@example.com'
        message = "Test notification"

        with self.assertRaises(ValueError) as context:
            NotificationService.send_notification(self.sender, invalid_email, message)

    def test_send_null_and_empty_message(self):
        recipient_email = 'testuser@example.com'

        with self.assertRaises(ValueError) as context:
            NotificationService.send_notification(self.sender, recipient_email, None)

        with self.assertRaises(ValueError) as context:
            NotificationService.send_notification(self.sender, recipient_email, "")

    def test_side_effects(self):
        recipient_email = 'testuser@example.com'
        message = "Test notification"

        # Send the notification
        NotificationService.send_notification(self.sender, recipient_email, message)

        # Retrieve the notifications and check the side effect (i.e., the notification queue)
        notifications = NotificationService.get_user_notifications(self.user)
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].title, message)
        self.assertEqual(notifications[0].recipient, self.user)
        self.assertEqual(notifications[0].sender, self.sender)

    def test_boundary(self):
        recipient_email = 'testuser@example.com'
        message = "A" * 1000  # Longest message allowed

        # Send the notification with a large message
        result = NotificationService.send_notification(self.sender, recipient_email, message)

        self.assertTrue(result)

        # Check if the notification is stored correctly in the queue
        notifications = NotificationService.get_user_notifications(self.user)
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].title, message)

class MyCourseModelTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create(
            name='instructor', password='password', role='Instructor' , email='instructor@gmail.com'
        )
        self.non_instructor = MyUser.objects.create(name='non_instructor', password='password', role='Student',
                                               email='student@gmail.com')

    def test_course_creation(self):
        course = MyCourse.objects.create(
            name="Test Course",
            instructor=self.user,
            room="101",
            time="10:00 AM - 12:00 PM"
        )
        self.assertEqual(course.name, "Test Course")
        self.assertEqual(course.instructor, self.user)
        self.assertEqual(course.room, "101")
        self.assertEqual(course.time, "10:00 AM - 12:00 PM")

    def test_course_requires_instructor(self):
        course = MyCourse.objects.create(name="Course without Instructor", room="Room B", time="11:00 AM")
        self.assertIsNone(course.instructor)

    def test_course_name_length(self):
        long_name = "A" * 101  # Name longer than the max allowed length (100 characters)
        with self.assertRaises(ValidationError):
            course = MyCourse(
                name=long_name,
                instructor=self.user,
                room="101",
                time="10:00 AM - 12:00 PM"
            )
            course.full_clean()

    def test_course_string_representation(self):
        course = MyCourse.objects.create(
            name="Test Course",
            instructor=self.user,
            room="101",
            time="10:00 AM - 12:00 PM"
        )
        self.assertEqual(str(course), "Test Course", msg="String representation of the course is incorrect")

    def test_course_update(self):
        course = MyCourse.objects.create(
            name="Old Course",
            instructor=self.user,
            room="101",
            time="10:00 AM - 12:00 PM"
        )
        # Update course information
        course.name = "Updated Course"
        course.room = "202"
        course.time = "2:00 PM - 4:00 PM"
        course.save()

        # Retrieve and verify the updated course
        updated_course = MyCourse.objects.get(id=course.id)
        self.assertEqual(updated_course.name, "Updated Course")
        self.assertEqual(updated_course.room, "202")
        self.assertEqual(updated_course.time, "2:00 PM - 4:00 PM")

    def test_multiple_courses_with_same_instructor(self):
        course1 = MyCourse.objects.create(
            name="Course 1",
            instructor=self.user,
            room="101",
            time="10:00 AM - 12:00 PM"
        )
        course2 = MyCourse.objects.create(
            name="Course 2",
            instructor=self.user,
            room="102",
            time="1:00 PM - 3:00 PM"
        )

        # Retrieve the courses taught by this instructor
        courses = self.user.courses.all()  # This uses the related_name='courses' from the ForeignKey field
        self.assertEqual(courses.count(), 2, msg="Instructor should have two courses")
        self.assertIn(course1, courses)
        self.assertIn(course2, courses)

class MyCourseFormTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            name="instructor", password="password", role="Instructor", email='instructor@gmail.com'
        )
    
    def test_valid_course_form(self):
        form_data = {
            "name": "Valid Course",
            "instructor": self.user.id,
            "room": "202",
            "time": "2:00 PM - 4:00 PM"
        }
        form = CourseForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_course_form_missing_fields(self):
        form_data = {
            "name": "",
            "instructor": self.user.id,
            "room": "",
            "time": ""
        }
        form = CourseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)

class EditUserViewTest(TestCase):
    def setUp(self):
        self.admin_user = MyUser.objects.create_user(
            name="admin",
            email="admin@example.com",
            password="adminpass",
            role="admin"
        )

        # Create a regular user to edit
        self.test_user = MyUser.objects.create_user(
            name="testuser",
            email="testuser@example.com",
            password="testpass",
            role="user"
        )
        self.client = Client()

        self.client.login(username="admin", password="adminpass")

    def test_get_edit_user_page(self):
        response = self.client.get(reverse('edit_user', args=[self.test_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/edit_user.html')
        self.assertEqual(response.context['user'], self.test_user)

    def test_edit_user_valid_data(self):
        response = self.client.post(
            reverse('edit_user', args=[self.test_user.id]),
            {
                'newName': 'Updated Name',
                'newPassword': 'newpassword123',
                'newContactInfo': 'newemail@example.com',
                'newRole': 'TA'
            }
        )
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.name, 'Updated Name')
        self.assertTrue(self.test_user.check_password('newpassword123'))  # Check password is updated
        self.assertEqual(self.test_user.email, 'testuser@example.com')  # Ensure email stays unchanged if not updated
        self.assertEqual(self.test_user.role, 'TA')
        self.assertRedirects(response, reverse('account_management'))

    def test_edit_user_partial_data(self):
        response = self.client.post(
            reverse('edit_user', args=[self.test_user.id]),
            {
                'newName': 'Partial Update',
            }
        )
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.name, 'Partial Update')
        self.assertEqual(self.test_user.email, 'testuser@example.com')  # Unchanged
        self.assertEqual(self.test_user.role, 'user')  # Unchanged
        self.assertRedirects(response, reverse('account_management'))

    def test_edit_user_invalid_user(self):
        response = self.client.get(reverse('edit_user', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_edit_user_unauthenticated_access(self):
        response = self.client.get(reverse('edit_user', args=[2]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Edit User:")


class DeleteUserViewTest(TestCase):
    def setUp(self):
        # Create a test admin user
        self.admin_user = MyUser.objects.create_user(
            name="admin",
            email="admin@example.com",
            password="adminpass",
            role="admin"
        )

        # Create a regular user to delete
        self.test_user = MyUser.objects.create_user(
            name="testuser",
            email="testuser@example.com",
            password="testpass",
            role="user"
        )

        self.client = Client()

        self.client.login(username="admin", password="adminpass")

    def test_get_confirm_delete_page(self):
        url = reverse('delete_user', args=[self.test_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/confirm_delete.html')
        self.assertEqual(response.context['user'], self.test_user)

    def test_delete_user_post_request(self):
        url = reverse('delete_user', args=[self.test_user.id])
        response = self.client.post(url)
        # Check that the user is deleted
        with self.assertRaises(MyUser.DoesNotExist):
            MyUser.objects.get(id=self.test_user.id)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account_management'))

    def test_delete_user_unauthenticated_access(self):
        self.client.logout()
        url = reverse('delete_user', args=[self.test_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_get_non_existent_user_confirm_page(self):
        url = reverse('delete_user', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_delete_user_unauthorized_access(self):
        # Log out the admin user
        self.client.logout()

        # Try to access the delete confirmation page
        url = reverse('delete_user', args=[self.test_user.id])
        response = self.client.get(url)

        # Ensure that the user is redirected to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))
        
class AuthServiceLoginUnitTests(TestCase):
    def setUp(self):
        self.user_data = {
            'name': 'test1',
            'email': 'test1@testing.com',
            'password': '123',
            'role': 'TA'
        }
        self.user = MyUser.objects.create_user(**self.user_data)
        self.mock_request = Mock()

    def test_successful_login_returns_true(self):
        result = AuthService.login(
            self.mock_request, 
            self.user_data['name'], 
            self.user_data['password']
        )
        
        self.assertTrue(result)

    def test_incorrect_password_returns_false(self):
        result = AuthService.login(
            self.mock_request, 
            self.user_data['name'], 
            'wrongpassword'
        )
        
        self.assertFalse(result)

    def test_nonexistent_user_returns_false(self):
        result = AuthService.login(
            self.mock_request, 
            'nonexistentuser', 
            'somepassword'
        )
        
        self.assertFalse(result)

    def test_empty_credentials_return_false(self):
        result = AuthService.login(
            self.mock_request
        )
        
        self.assertFalse(result)

    def test_username_is_case_sensitive(self):
        result = AuthService.login(
            self.mock_request, 
            self.user_data['name'].upper(), 
            self.user_data['password']
        )
        
        self.assertFalse(result)
