from django.test import TestCase
from TASchedulerApp.models import MyCourse, MyUser
from unittest.mock import Mock, patch
from django.contrib.auth import get_user_model
from TASchedulerApp.service.auth_service import AuthService
from TASchedulerApp.service.course_service import CourseService, assign_instructor_and_tas


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
