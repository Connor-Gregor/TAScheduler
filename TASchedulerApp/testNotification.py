from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model

from .models import Notification

User = get_user_model()

class SendNotificationViewTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            email='sender@gmail.com',
            name='sender',
            password='testpassword',
            role='Instructor'
        )

        # Create a recipient user
        self.recipient = User.objects.create_user(
            email='recipient@gmail.com',
            name='recipient',
            password='testpassword',
            role='TA'
        )

        self.client = Client()
        self.client.login(username='sender', password='testpassword')

        self.url = reverse('send_notifications')

    def test_get_send_notification_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'instructor/send_notifications.html')

    def test_valid_notification(self):
        data = {
            'title': 'Test Notification',
            'recipient_email': 'recipient@example.com'
        }
        response = self.client.post(self.url, data)

        notification = Notification.objects.first()
        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.sender, self.sender.name)
        self.assertEqual(notification.recipient, self.recipient)

        self.assertRedirects(response, reverse('notifications'))

    def test_invalid_recipient_email(self):
        data = {
            'title': 'Test Notification',
            'recipient_email': 'invalid@example.com'
        }
        response = self.client.post(self.url, data, follow=True)

        # Notification should not be created
        self.assertEqual(Notification.objects.count(), 0)

        # Check for the error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Invalid recipient email!" in str(message) for message in messages))

        # Ensure we are redirected back to the form
        self.assertRedirects(response, self.url)
    def test_missing_title(self):
        data = {
            'title': '',
            'recipient_email': 'recipient@example.com'
        }
        response = self.client.post(self.url, data)

        # Depending on your application's logic, decide if this should create a notification or not.
        # Here, we'll assume a notification with an empty title is acceptable.

        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.title, '')
        self.assertEqual(notification.recipient, self.recipient)
        self.assertRedirects(response, reverse('notifications'))

    def test_missing_email(self):
        data = {
            'title': 'Test Notification',
            'recipient_email': ''
        }
        response = self.client.post(self.url, data, follow=True)

        # Notification should not be created
        self.assertEqual(Notification.objects.count(), 0)

        # Check for the error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Invalid recipient email!" in str(message) for message in messages))

        # Ensure we are redirected back to the form
        self.assertRedirects(response, self.url)
