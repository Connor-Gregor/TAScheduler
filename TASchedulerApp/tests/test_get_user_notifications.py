from django.test import TestCase
from TASchedulerApp.models import Notification, MyUser
from TASchedulerApp.service.notification_service import NotificationService
from datetime import datetime, timedelta


#This is for the old notification system that wasn't needed, dont run/use
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

    # notification2 is sent to user1 AFTER notification1, so notification2 should come first
    def test__ordering(self):
        notifications = NotificationService.get_user_notifications(self.user1)
        self.assertEqual(notifications[0], self.notification2, "Latest notification should come first")
        self.assertEqual(notifications[1], self.notification1, "Oldest notification should come last")

    # no notifications are sent to user2
    def test_no_notifications(self):
        notifications = NotificationService.get_user_notifications(self.user2)
        self.assertEqual(len(notifications), 0, "Should return no notifications for user2")
