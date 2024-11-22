from django.test import TestCase
from argparse import ArgumentTypeError
from unittest.mock import Mock
import unittest
from courseservice import CourseService
from TASchedulerApp.utils.Notification import notification


# Create your tests here.

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
