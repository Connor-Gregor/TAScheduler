from django.test import TestCase, RequestFactory
from TASchedulerApp.models import MyCourse, MyUser, Notification
from unittest.mock import Mock, patch
from django.contrib.auth import get_user_model
from TASchedulerApp.service.auth_service import AuthService
from TASchedulerApp.service.course_service import CourseService, assign_instructor_and_tas
from TASchedulerApp.service.edit_user_service import update_user_profile
from TASchedulerApp.service.account_service import AccountService
from TASchedulerApp.service.notification_service import NotificationService
from datetime import datetime, timedelta

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

    def test_username_is_case_sensitive(self):
        result = AuthService.login(
            self.mock_request, 
            self.user_data['name'].upper(), 
            self.user_data['password']
        )
        
        self.assertFalse(result)
        
class CourseServiceTest(TestCase):

    def setUp(self):
        self.user_data = {
            'name': 'Boyland',
            'email': 'test1@testing.com',
            'password': '123',
            'role': 'Instructor',
            'office_hours': '8:00 AM',
            'office_location': 'Room 100'
        }
        self.instructor = MyUser.objects.create_user(**self.user_data)
        self.course = MyCourse.objects.create(
            name="CS 351",
            instructor=self.instructor,
            room="Room 200",
            time="10:00 AM"
        )

    def test_edit_course_name(self):
        new_data = {'new_name': 'Chang'}
        CourseService.edit_course(self.course.id, new_data)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, 'Chang')

    def test_edit_course_instructor(self):
        self.user_data = {
            'name': 'John1',
            'email': 'test2@testing.com',
            'password': '1234',
            'role': 'Instructor',
            'office_hours': '8:00 AM',
            'office_location': 'Room 100'
        }
        self.instructor1 = MyUser.objects.create_user(**self.user_data)
        new_data = {'new_instructor': self.instructor1}
        CourseService.edit_course(self.course.id, new_data)
        self.course.refresh_from_db()
        self.assertEqual(self.course.instructor, self.instructor1)

    def test_edit_course_room(self):
        new_data = {'new_room': 'Room 202'}
        CourseService.edit_course(self.course.id, new_data)
        self.course.refresh_from_db()
        self.assertEqual(self.course.room, 'Room 202')

    def test_edit_course_time(self):
        new_data = {'new_time': '2:00 PM'}
        CourseService.edit_course(self.course.id, new_data)
        self.course.refresh_from_db()
        self.assertEqual(self.course.time, '2:00 PM')

    def test_edit_multiple_fields(self):
        self.user_data = {
            'name': 'Boyland2',
            'email': 'test2@testing.com',
            'password': '123',
            'role': 'Instructor',
            'office_hours': '8:00 AM',
            'office_location': 'Room 100'
        }
        self.instructor1 = MyUser.objects.create_user(**self.user_data)
        new_data = {
            'new_name': 'John',
            'new_instructor': self.instructor1,
            'new_room': 'Room 303',
            'new_time': '4:00 PM'
        }
        CourseService.edit_course(self.course.id, new_data)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, 'John')
        self.assertEqual(self.course.instructor, self.instructor1)
        self.assertEqual(self.course.room, 'Room 303')
        self.assertEqual(self.course.time, '4:00 PM')

    def test_edit_no_changes(self):
        original_data = {
            'name': self.course.name,
            'instructor': self.course.instructor,
            'room': self.course.room,
            'time': self.course.time
        }
        CourseService.edit_course(self.course.id, {})
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, original_data['name'])
        self.assertEqual(self.course.instructor, original_data['instructor'])
        self.assertEqual(self.course.room, original_data['room'])
        self.assertEqual(self.course.time, original_data['time'])

class UpdateUserProfileTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            name="OldName",
            home_address="123 Old St",
            phone_number="1234567890",
            email="test@example.com",
            office_hours="today",
            office_location="E123",
            password="oldpassword"
        )
        # Create a mock request object
        self.mock_request = patch('django.http.HttpRequest').start()

    @patch('TASchedulerApp.service.edit_user_service.update_session_auth_hash')
    def test_update_name(self, mock_update_session_auth_hash):
        update_user_profile(
            request=self.mock_request,
            user=self.user,
            name="NewName",
            home_address=self.user.home_address,
            phone_number=self.user.phone_number,
            office_hours=self.user.office_hours,
            office_location=self.user.office_location,
            password=None
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "NewName")
        self.assertEqual(self.user.home_address, "123 Old St")
        self.assertEqual(self.user.phone_number, "1234567890")
        mock_update_session_auth_hash.assert_not_called()

    @patch('TASchedulerApp.service.edit_user_service.update_session_auth_hash')
    def test_update_home_address(self, mock_update_session_auth_hash):
        update_user_profile(
            request=self.mock_request,
            user=self.user,
            name=self.user.name,
            home_address="456 New Ave",
            phone_number=self.user.phone_number,
            office_hours=self.user.office_hours,
            office_location=self.user.office_location,
            password=None
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "OldName")
        self.assertEqual(self.user.home_address, "456 New Ave")
        mock_update_session_auth_hash.assert_not_called()

    @patch('TASchedulerApp.service.edit_user_service.update_session_auth_hash')
    def test_update_phone_number(self, mock_update_session_auth_hash):
        update_user_profile(
            request=self.mock_request,
            user=self.user,
            name=self.user.name,
            home_address=self.user.home_address,
            phone_number="0987654321",
            office_hours=self.user.office_hours,
            office_location=self.user.office_location,
            password=None
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, "0987654321")
        mock_update_session_auth_hash.assert_not_called()

    @patch('TASchedulerApp.service.edit_user_service.update_session_auth_hash')
    def test_update_password(self, mock_update_session_auth_hash):
        update_user_profile(
            request=self.mock_request,
            user=self.user,
            name=self.user.name,
            home_address=self.user.home_address,
            phone_number=self.user.phone_number,
            office_hours=self.user.office_hours,
            office_location=self.user.office_location,
            password="newpassword"
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword"))
        mock_update_session_auth_hash.assert_called_once_with(self.mock_request, self.user)

    @patch('TASchedulerApp.service.edit_user_service.update_session_auth_hash')
    def test_no_changes(self, mock_update_session_auth_hash):
        update_user_profile(
            request=self.mock_request,
            user=self.user,
            name=self.user.name,
            home_address=self.user.home_address,
            phone_number=self.user.phone_number,
            office_hours=self.user.office_hours,
            office_location=self.user.office_location,
            password=None
        )
        self.user.refresh_from_db()
        # Ensure no changes were made
        self.assertEqual(self.user.name, "OldName")
        self.assertEqual(self.user.home_address, "123 Old St")
        self.assertEqual(self.user.phone_number, "1234567890")
        mock_update_session_auth_hash.assert_not_called()

    @patch('TASchedulerApp.service.edit_user_service.update_session_auth_hash')
    def test_update_office_hours(self, mock_update_session_auth_hash):
        update_user_profile(
            request=self.mock_request,
            user=self.user,
            name=self.user.name,
            home_address=self.user.home_address,
            phone_number=self.user.phone_number,
            office_hours="Fridays",
            office_location=self.user.office_location,
            password=None
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.office_hours, "Fridays")
        mock_update_session_auth_hash.assert_not_called()

    @patch('TASchedulerApp.service.edit_user_service.update_session_auth_hash')
    def test_update_office_location(self, mock_update_session_auth_hash):
        update_user_profile(
            request=self.mock_request,
            user=self.user,
            name=self.user.name,
            home_address=self.user.home_address,
            phone_number=self.user.phone_number,
            office_hours=self.user.office_hours,
            office_location="Ur moms house",
            password=None
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.office_location, "Ur moms house")
        mock_update_session_auth_hash.assert_not_called()

class NotificationServiceTestCase(TestCase):
    def setUp(self):
        self.user1 = MyUser.objects.create(email="user1@example.com", name="User One")
        self.user2 = MyUser.objects.create(email="user2@example.com", name="User Two")

        self.notification1 = Notification.objects.create(
            title="First Notification",
            sender=self.user2,
            recipient=self.user1,
            time_received=datetime.now()
        )
        self.notification2 = Notification.objects.create(
            title="Second Notification",
            sender=self.user2,
            recipient=self.user1,
            time_received=datetime.now() + timedelta(minutes=5)
        )

    # exactly two notifications are will be returned
    def test_returns_correct_notifications(self):
        notifications = NotificationService.get_user_notifications(self.user1)
        self.assertEqual(len(notifications), 2, "Should return exactly 2 notifications for user1")
        self.assertIn(self.notification1, notifications, "Notification1 should be in the results")
        self.assertIn(self.notification2, notifications, "Notification2 should be in the results")

    # no notifications are sent to user2
    def test_no_notifications(self):
        notifications = NotificationService.get_user_notifications(self.user2)
        self.assertEqual(len(notifications), 0, "Should return no notifications for user2")

class UnitTestNotificationService(TestCase):
    def setUp(self):

        self.sender = MyUser.objects.create_user(
            name="Sender User",
            email="sender@example.com",
            role="Instructor",
            password="password123"
        )
        self.recipient = MyUser.objects.create_user(
            name="Recipient User",
            email="recipient@example.com",
            role="TA",
            password="password123"
        )

    def test_send_notification_success(self):
        NotificationService.send_notification(
            sender=self.sender.name,
            recipient_email=self.recipient.email,
            title="Test Notification"
        )

        notification = Notification.objects.filter(
            sender=self.sender.name,
            recipient=self.recipient,
            title="Test Notification"
        ).first()

        self.assertIsNotNone(notification, "Notification should be created.")
        self.assertEqual(notification.title, "Test Notification")
        self.assertEqual(notification.sender, self.sender.name)
        self.assertEqual(notification.recipient, self.recipient)

    def test_send_notification_invalid_email(self):
        with self.assertRaises(ValueError):
            NotificationService.send_notification(
                sender=self.sender.name,
                recipient_email="nonexistent@example.com",
                title="Invalid Email Notification"
            )

    def test_send_notification_missing_title(self):
        with self.assertRaises(ValueError):
            NotificationService.send_notification(
                sender=self.sender.name,
                recipient_email=self.recipient.email,
                title=""
            )

    def test_get_user_notifications_empty(self):
        notifications = NotificationService.get_user_notifications(self.recipient)

        self.assertEqual(len(notifications), 0, "There should be no notifications.")

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

class UpdateUserProfileTestCase(TestCase):

    def setUp(self):
        # Create a user to test on
        self.user = MyUser.objects.create_user(
            email='test@example.com',
            password='oldpassword',
            name='Test User',
            home_address='123 Main St',
            phone_number='1234567890',
            office_hours='9-5',
            office_location='Room 101'
        )

        # Create a request object
        self.factory = RequestFactory()
        self.request = self.factory.post('/update-profile/', {
            'name': 'Updated User',
            'home_address': '456 Elm St',
            'phone_number': '0987654321',
            'office_hours': '10-6',
            'office_location': 'Room 102',
            'password': 'newpassword'
        })

        # Set the user as the logged-in user for the request
        self.request.user = self.user

    def test_update_name(self):
        # Test if the name is updated
        updated_name = 'Updated User'
        update_user_profile(self.request, self.user, updated_name, self.user.home_address, self.user.phone_number, '', self.user.office_hours, self.user.office_location)

        # Reload the user from the database
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, updated_name)

    def test_update_home_address(self):
        # Test if the home_address is updated
        updated_address = '456 Elm St'
        update_user_profile(self.request, self.user, self.user.name, updated_address, self.user.phone_number, '', self.user.office_hours, self.user.office_location)

        # Reload the user from the database
        self.user.refresh_from_db()

        self.assertEqual(self.user.home_address, updated_address)

    def test_update_phone_number(self):
        # Test if the phone_number is updated
        updated_phone = '0987654321'
        update_user_profile(self.request, self.user, self.user.name, self.user.home_address, updated_phone, '', self.user.office_hours, self.user.office_location)

        # Reload the user from the database
        self.user.refresh_from_db()

        self.assertEqual(self.user.phone_number, updated_phone)

    def test_update_office_hours(self):
        # Test if office_hours are updated
        updated_hours = '10-6'
        update_user_profile(self.request, self.user, self.user.name, self.user.home_address, self.user.phone_number, '', updated_hours, self.user.office_location)

        # Reload the user from the database
        self.user.refresh_from_db()

        self.assertEqual(self.user.office_hours, updated_hours)

    def test_update_office_location(self):
        # Test if office_location is updated
        updated_location = 'Room 102'
        update_user_profile(self.request, self.user, self.user.name, self.user.home_address, self.user.phone_number, '', self.user.office_hours, updated_location)

        # Reload the user from the database
        self.user.refresh_from_db()

        self.assertEqual(self.user.office_location, updated_location)


    @patch('TASchedulerApp.service.edit_user_service.update_session_auth_hash')  # Mock update_session_auth_hash
    def test_update_session_auth_hash_called_on_password_change(self, mock_update_session_auth_hash):
        # Call the method with a new password
        update_user_profile(self.request, self.user, self.user.name, self.user.home_address, self.user.phone_number,
                            'newpassword', self.user.office_hours, self.user.office_location)

        # Check if update_session_auth_hash was called
        mock_update_session_auth_hash.assert_called_once_with(self.request, self.user)

class CourseServiceAssignTests(TestCase):
    def setUp(self):

        self.user_data = {
            'name': 'test1',
            'email': 'test1@testing.com',
            'password': '123',
            'role': 'TA',
            'office_hours': '10:00 AM',
            'office_location': 'Room 101'
        }
        self.user_data2 = {
            'name': 'test2',
            'email': 'test2@testing.com',
            'password': '123',
            'role': 'Instructor',
            'office_hours': '10:00 AM',
            'office_location': 'Room 101'
        }
        self.user = MyUser.objects.create_user(**self.user_data)
        self.instructor = MyUser.objects.create_user(**self.user_data2)
        self.course = MyCourse.objects.create(
            name="CS 351",
            instructor=self.instructor,
            room="Room 200",
            time="10:00 AM"
        )

        self.mock_request = Mock()

    def test_no_course(self):
        result = assign_instructor_and_tas(course_id=9999, instructor_id=self.instructor.id, ta_id=self.user.id)
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Course not found.")

    def test_no_instructor(self):
        result = assign_instructor_and_tas(course_id=self.course.id, instructor_id=9999, ta_id=self.user.id)
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Instructor or TA not found.")

    def test_no_instructor_and_TA(self):
        result = assign_instructor_and_tas(course_id=self.course.id, instructor_id=9999, ta_id=9999)
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Instructor or TA not found.")

    def test_no_course_and_TA(self):
        result = assign_instructor_and_tas(course_id=9999, instructor_id=self.instructor.id, ta_id=9999)
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Course not found.")

    def test_no_course_and_Instructor(self):
        result = assign_instructor_and_tas(course_id=9999, instructor_id=9999, ta_id=self.user.id)
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Course not found.")

    def test_no_anything(self):
        result = assign_instructor_and_tas(course_id=9999, instructor_id=9999, ta_id=9999)
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Course not found.")

    def test_no_ta(self):
        result = assign_instructor_and_tas(course_id=self.course.id, instructor_id=self.instructor.id,ta_id=9999)
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Instructor or TA not found.")

    def test_error_course(self):
        result = assign_instructor_and_tas(course_id="hello", instructor_id=self.instructor.id,ta_id=self.user.id)
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Field 'id' expected a number but got 'hello'.")

    def test_error_instructor(self):
        result = assign_instructor_and_tas(course_id=self.course.id, instructor_id="hi",ta_id=self.user.id)
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Field 'id' expected a number but got 'hi'.")

    def test_error_ta(self):
        result = assign_instructor_and_tas(course_id=self.course.id, instructor_id=self.instructor.id,ta_id="bye")
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Field 'id' expected a number but got 'bye'.")

    def test_error_course_no_ta(self):
        result = assign_instructor_and_tas(course_id="hello", instructor_id=self.instructor.id,ta_id=9999)
        self.assertEqual(result['message'], "Field 'id' expected a number but got 'hello'.")

    def test_error_course_no_instructor(self):
        result = assign_instructor_and_tas(course_id="hello", instructor_id=9999, ta_id=self.user.id)
        self.assertEqual(result['message'], "Field 'id' expected a number but got 'hello'.")

    def test_error_ta_no_course(self):
        result = assign_instructor_and_tas(course_id=9999, instructor_id=self.instructor.id, ta_id="bye")
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Course not found.")

    def test_error_ta_no_instructor(self):
        result = assign_instructor_and_tas(course_id=self.course.id, instructor_id=9999, ta_id="bye")
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Instructor or TA not found.")

    def test_error_instructor_no_ta(self):
        result = assign_instructor_and_tas(course_id=self.course.id, instructor_id="hi", ta_id=9999)
        self.assertEqual(result['message'], "Field 'id' expected a number but got 'hi'.")

    def test_error_instructor_no_course(self):
        result = assign_instructor_and_tas(course_id=9999, instructor_id="hi", ta_id=self.user.id)
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Course not found.")

    def test_error_instructor_error_course(self):
        result = assign_instructor_and_tas(course_id="hello", instructor_id="hi", ta_id=self.user.id)
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Field 'id' expected a number but got 'hello'.")

    def test_error_ta_error_course(self):
        result = assign_instructor_and_tas(course_id="hello", instructor_id=self.instructor.id, ta_id="bye")
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Field 'id' expected a number but got 'hello'.")

    def test_error_ta_error_course_no_instructor(self):
        result = assign_instructor_and_tas(course_id="hello", instructor_id=9999, ta_id="bye")
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Field 'id' expected a number but got 'hello'.")

    def test_error_ta_error_instructor(self):
        result = assign_instructor_and_tas(course_id=self.course.id, instructor_id="hi", ta_id="bye")
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Field 'id' expected a number but got 'hi'.")

    def test_successful_assignment(self):
        result = assign_instructor_and_tas(course_id=self.course.id, instructor_id=self.instructor.id,ta_id=self.user.id)
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], "Assignments updated successfully.")
        self.course.refresh_from_db()
        self.assertEqual(self.course.instructor.id, self.instructor.id)
        self.assertIn(self.user, self.course.tas.all())

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