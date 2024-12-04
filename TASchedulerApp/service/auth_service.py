from django.contrib.auth import login
from TASchedulerApp.models import MyUser

class AuthService:
    @staticmethod
    def login(request, name, password):
        try:
            user = MyUser.objects.get(name=name)
            if user.check_password(password):
                login(request, user)
                return True
        except MyUser.DoesNotExist:
            pass
        return False