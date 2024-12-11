from django.test import TestCase
from TASchedulerApp.models import MyCourse, MyUser
from unittest.mock import Mock, patch
from django.contrib.auth import get_user_model
from TASchedulerApp.service.auth_service import AuthService
from TASchedulerApp.service.course_service import CourseService, assign_instructor_and_tas
from TASchedulerApp.service.edit_user_service import update_user_profile


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
        self.course = MyCourse.objects.create(
            name="CS 351",
            instructor="Boyland",
            room="Room 200",
            time="10:00 AM"
        )

    def test_edit_course_name(self):
        new_data = {'new_name': 'Chang'}
        CourseService.edit_course(self.course.id, new_data)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, 'Chang')

    def test_edit_course_instructor(self):
        new_data = {'new_instructor': 'John'}
        CourseService.edit_course(self.course.id, new_data)
        self.course.refresh_from_db()
        self.assertEqual(self.course.instructor, 'John')

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
        new_data = {
            'new_name': 'John',
            'new_instructor': 'Boyland',
            'new_room': 'Room 303',
            'new_time': '4:00 PM'
        }
        CourseService.edit_course(self.course.id, new_data)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, 'John')
        self.assertEqual(self.course.instructor, 'Boyland')
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
            password=None
        )
        self.user.refresh_from_db()
        # Ensure no changes were made
        self.assertEqual(self.user.name, "OldName")
        self.assertEqual(self.user.home_address, "123 Old St")
        self.assertEqual(self.user.phone_number, "1234567890")
        mock_update_session_auth_hash.assert_not_called()