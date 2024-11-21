import unittest
from TASchedulerApp.utils.Notification import notification

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

