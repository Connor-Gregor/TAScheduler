from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import Group
from .forms import RegistrationForm
from django.utils.decorators import method_decorator
from .decorators import role_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import MyUser


# Create your views here.
class Login(View):
    def get(self,request):
        return render(request, "common/login.html")

    def post(self, request):
        name = request.POST['username']
        password = request.POST['password']

        try:
            # Retrieve user by 'name' field (custom user model field)
            user = MyUser.objects.get(name=name)

            # Check if the password matches
            if user.check_password(password):
                login(request, user)  # Log the user in
                return redirect('dashboard')
            else:
                # Password incorrect
                return render(request, "common/login.html", {"message": "Invalid username or password1"})

        except MyUser.DoesNotExist:
            # User not found
            return render(request, "common/login.html", {"message": "Invalid username or password"})
class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        context = {
            'user': user,
            'user_role': user.role  # Pass the user's role to the template
        }
        return render(request, 'dashboard.html', context)
class Register(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'common/register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data['role']
            user.is_approved = True  # Or set to False if you require approval
            user.save()
            return redirect('login')
        else:
            return render(request, 'common/register.html', {'form': form})
class CreateCourseView(LoginRequiredMixin, View):
    @method_decorator(role_required(allowed_roles=['Administrator']))
    def get(self, request):
        # Implementation for GET request
        return render(request, 'admin/create_course.html')

    @method_decorator(role_required(allowed_roles=['Administrator']))
    def post(self, request):
        # Implementation for POST request
        pass

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        return render(request, 'common/profile.html', {'user': user})

    def post(self, request):
        # Handle form submissions to update profile information
        pass

class NotificationView(View):
    def get(self, request):
        # Logic for fetching and displaying notifications
        return render(request, 'common/notifications.html')