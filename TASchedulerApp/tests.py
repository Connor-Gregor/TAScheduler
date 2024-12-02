from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase, Client
from TASchedulerApp.services import AccountService
import unittest
from unittest.mock import Mock, patch
from argparse import ArgumentTypeError
from courseservice import CourseService
from TASchedulerApp.utils.Notification import notification


# Create your tests here.

class TestRedirectToDashboard(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'John Burgerton'
        self.password = '123abc'

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
            'username': self.username,
            'password': self.password
        })

        mock_authenticate.assert_called_once_with(
            username=self.username,
            password=self.password
        )
        self.assertEqual(response.status_code, 302)

    def test_bad_login_username(self):
        # Test that an error message is shown for invalid username
        response = self.client.post('/', {
            'username': 'wrong_username',
            'password': self.password
        })
        self.assertContains(response, "User does not exist")

    def test_bad_login_password(self):
        # Test that an error message is shown for incorrect password
        response = self.client.post('/', {
            'username': self.username,
            'password': 'wrong_password'
        })
        self.assertContains(response, "Incorrect password")

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

# courseId and instructorId exist in the database
# instructorId corresponds to an active instructor
# courseId (in): Identifier for the course
# instructorId (in): Identifier for the instructor
class TestAssignInstructor(unittest.TestCase):
    def setUp(self):
        self.service = CourseService()
        self.service.find_course = Mock()
        self.service.find_instructor = Mock()
        self.service.active_instructor = Mock()

    def test_noCourseId(self):
        with self.assertRaises(ArgumentTypeError, msg="Course ID must be provided"):
            self.service.assign_instructor(None, 1)

    def test_noInstructorId(self):
        with self.assertRaises(ArgumentTypeError, msg="Instructor ID must be provided"):
            self.service.assign_instructor(1, None)

    def test_CourseIdNotExist(self):
        self.service.find_course.return_value = False
        with self.assertRaises(TypeError, msg="Course does not exist"):
            self.service.assign_instructor(99999999, 1)

    def test_InstructorIdNotExist(self):
        self.service.find_course.return_value = True
        self.service.find_instructor.return_value = False
        with self.assertRaises(TypeError, msg="Instructor does not exist"):
            self.service.assign_instructor(1, 99999999)

    def test_InstructorNotActive(self):
        self.service.find_course.return_value = True
        self.service.find_instructor.return_value = True
        self.service.active_instructor.return_value = False
        with self.assertRaises(TypeError, msg="Instructor is not active"):
            self.service.assign_instructor(1, 3)

    def test_InstructorAssigned(self):
        self.service.find_course.return_value = True
        self.service.find_instructor.return_value = True
        self.service.active_instructor.return_value = True
        self.service.assign_instructor = Mock()
        self.service.assign_instructor(1, 3)
        self.service.assign_instructor.assert_called_with(1, 3)

class TestNotification(unittest.TestCase):
  def test_validID(self):
    recipient_id = 123
    message = "Test notification"

    result = notification().sendNotification(recipient_id, message)

    assert result is True
    assert notification().getNotificationQueue(recipient_id) == ["Test notification"]

  def test_send_invalid_recipient(self):
    recipient_id = -1  # Invalid ID
    message = "Test notification"

    try:
      notification().sendNotification(recipient_id, message)
    except ValueError as e:
      assert str(e) == "Invalid recipient ID"

  def test_send_null_and_empty_message(self):
    recipient_id = 123

    try:
      notification().sendNotification(recipient_id, None)
    except ValueError as e:
      assert str(e) == "Message cannot be null or empty"

    try:
      notification().sendNotification(recipient_id, "")
    except ValueError as e:
      assert str(e) == "Message cannot be null or empty"

  def test_side_effects(self):
    recipient_id = 123
    message = "Test notification"

    notification().sendNotification(recipient_id, message)

    queue = notification().getNotificationQueue(recipient_id)
    assert len(queue) == 1
    assert queue[0] == message

  def test_boundary(self):
    recipient_id = 1  # Smallest valid ID
    message = "A" * 1000  # Longest message

    result = notification().sendNotification(recipient_id, message)

    assert result is True
    assert notification().getNotificationQueue(recipient_id) == [message]

