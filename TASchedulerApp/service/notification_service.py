from TASchedulerApp.models import Notification, MyUser

class NotificationService:
    @staticmethod
    def send_notification(sender, recipient_email, title):
        try:
            recipient = MyUser.objects.get(email=recipient_email)
        except MyUser.DoesNotExist:
            raise ValueError("Invalid recipient email!")

        if not title:
            raise ValueError("Title cannot be empty!")

        Notification.objects.create(
            title=title,
            sender=sender,
            recipient=recipient
        )
        return True

    @staticmethod
    def get_user_notifications(user):
        return Notification.objects.filter(recipient=user).order_by('-time_received')
