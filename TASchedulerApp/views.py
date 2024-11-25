from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import Group
from .forms import RegistrationForm
from .models import MyUser
from django.utils.decorators import method_decorator
from .decorators import role_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
class Login(View):
    def get(self,request):
        return render(request, "common/login.html")

    def post(self, request):
        name = request.POST['name']
        password = request.POST['password']

        # Check if username exists
        #Change MyUser to name of class from models.py + include from .models import MyUser at the top
        user = authenticate(request, username=name, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
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
            # Assign the user to a group based on their role
            if user.role == 'Instructor':
                group, _ = Group.objects.get_or_create(name='Instructor')
            else:
                group, _ = Group.objects.get_or_create(name='TA')
            user.groups.add(group)
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
