from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import CourseForm, RegistrationForm
from django.utils.decorators import method_decorator
from .decorators import role_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import MyCourse, MyUser, Notification
from .service.account_service import AccountService
from .service.auth_service import AuthService
from .service.course_service import CourseService, assign_instructor_and_tas
from .service.notification_service import NotificationService

# Create your views here.

class Login(View):
    def get(self, request):
        return render(request, "common/login.html")

    def post(self, request):
        name = request.POST['username']
        password = request.POST['password']

        if AuthService.login(request, name, password):
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
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            password = form.cleaned_data['password1']  # This is the password to hash

            # Call AccountService.create_account to handle user creation and password hashing
            AccountService.create_account(name, email, role, password)

            # Redirect back to the account management page after admin makes the new account
            return redirect('account_management')
        else:
            return render(request, 'common/register.html', {'form': form})


class CreateCourseView(LoginRequiredMixin, View):
    @method_decorator(role_required(allowed_roles=['Administrator']))
    def get(self, request):
        courses = MyCourse.objects.all()
        return render(request, 'admin/course_management.html', {'courses': courses})

    @method_decorator(role_required(allowed_roles=['Administrator']))
    def post(self, request):
        # Implementation for POST request
        pass


class CreateCourse(LoginRequiredMixin, View):
    @method_decorator(role_required(allowed_roles=['Administrator']))
    def get(self, request):
        form = CourseForm()
        return render(request, 'admin/create_course.html', {'form': form})

    def post(self, request):
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            return redirect('course_management')
        else:
            return render(request, 'admin/create_course.html', {'form': form})


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        return render(request, 'common/profile.html', {'user': user})

    def post(self, request):
        # Handle form submissions to update profile information
        pass


class NotificationView(View):
    def get(self, request):
        return render(request, 'common/notifications.html')


class ManageUsers(LoginRequiredMixin, View):
    def get(self, request):
        users = MyUser.objects.filter(role__in=['Instructor', 'TA'])
        return render(request, 'admin/manage_users.html', {'users': users})


class EditUser(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = get_object_or_404(MyUser, id=user_id)
        return render(request, 'admin/edit_user.html', {'user': user})

    def post(self, request, user_id):
        new_data = {
            'new_name': request.POST.get('newName'),
            'new_password': request.POST.get('newPassword'),
            'new_contact_info': request.POST.get('newContactInfo'),
            'new_role': request.POST.get('newRole'),
        }
        try:
            AccountService.edit_user(user_id, {k: v for k, v in new_data.items() if v})
            return redirect('account_management')
        except Exception as e:
            return render(request, 'admin/edit_user.html', {'error': str(e)})


class DeleteUser(LoginRequiredMixin, View):
    def post(self, request, user_id):
        try:
            AccountService.delete_user(user_id)
            return redirect('account_management')
        except Exception as e:
            return render(request, 'admin/confirm_delete.html', {'error': str(e)})

    def get(self, request, user_id):
        user = get_object_or_404(MyUser, id=user_id)
        return render(request, 'admin/confirm_delete.html', {'user': user})


class EditCourse(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = get_object_or_404(MyCourse, id=course_id)
        return render(request, 'admin/edit_course.html', {'course': course})

    def post(self, request, course_id):
        new_data = {
            'new_name': request.POST.get('newName'),
            'new_instructor': request.POST.get('newInstructor'),
            'new_room': request.POST.get('newRoom'),
            'new_time': request.POST.get('newTime'),
        }
        try:
            CourseService.edit_course(course_id, {k: v for k, v in new_data.items() if v})
            return redirect('course_management')
        except Exception as e:
            return render(request, 'admin/edit_course.html', {'error': str(e)})


class Notifications(LoginRequiredMixin, View):
    def get(self, request):
        notificationsList = NotificationService.get_user_notifications(request.user)
        return render(request, 'common/notifications.html', {'notifications': notificationsList})


class SendNotification(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'instructor/send_notifications.html')

    def post(self, request):
        title = request.POST.get('title')
        sender = request.user.name
        recipient_email = request.POST.get('recipient_email')

        try:
            NotificationService.send_notification(sender, recipient_email, title)
            messages.success(request, "Notification sent successfully!")
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('send_notifications')

        return redirect('notifications')

def is_admin(user):
    return user.is_superuser

@login_required
def assign_users_to_course(request, course_id):
    course = get_object_or_404(MyCourse, id=course_id)
    instructors = MyUser.objects.filter(role='Instructor')
    tas = MyUser.objects.filter(role='TA')

    if request.method == 'POST':
        instructor_id = request.POST.get('instructor')
        ta_id = request.POST.get('tas')

        print(f"Received instructor ID: {instructor_id}")
        print(f"Received TA ID: {ta_id}")

        result = assign_instructor_and_tas(course_id, instructor_id, ta_id)

        print(f"Service result: {result}")

        if result['success']:
            return redirect('course_management')
        else:
            return render(request, 'admin/assign_users.html', {
                'course': course,
                'instructors': instructors,
                'tas': tas,
                'error': result['message']
            })

    return render(request, 'admin/assign_users.html', {
        'course': course,
        'instructors': instructors,
        'tas': tas
    })
