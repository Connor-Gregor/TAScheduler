from django.test import TestCase
from TASchedulerApp.models import MyCourse, MyUser
from unittest.mock import Mock, patch
from django.contrib.auth import get_user_model
from TASchedulerApp.service.course_service import CourseService, assign_instructor_and_tas


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

