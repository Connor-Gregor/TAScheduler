from django.test import TestCase
from TASchedulerApp.models import MyUser, Notification
from TASchedulerApp.service.notification_service import NotificationService


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
