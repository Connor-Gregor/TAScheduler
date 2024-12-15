from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import CourseForm, RegistrationForm, CourseAssignmentForm
from django.utils.decorators import method_decorator
from .decorators import role_required
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import MyCourse, MyUser, Notification
from .service.account_service import AccountService
from .service.auth_service import AuthService
from .service.course_service import CourseService, assign_instructor_and_tas
from .service.notification_service import NotificationService
from .service.edit_user_service import update_user_profile

from .forms import LabSectionForm
from .decorators import role_required
from .models import LabSection


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


@method_decorator(login_required, name='dispatch')
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
        form = CourseForm(instance=course)  # Assuming you have a CourseForm
        return render(request, 'admin/edit_course.html', {'form': form})

    def post(self, request, course_id):
        course = get_object_or_404(MyCourse, id=course_id)
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_management')
        return render(request, 'admin/edit_course.html', {'form': form})

def delete_course(request, course_id):
    if request.method == "POST":
        course = get_object_or_404(MyCourse, id=course_id)
        course.delete()
        messages.success(request, "Course deleted successfully.")
        return redirect('course_management')

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


@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        name = request.POST.get('name', user.name)
        home_address = request.POST.get('home_address', user.home_address)
        phone_number = request.POST.get('phone_number', user.phone_number)
        password = request.POST.get('password', None)
        office_hours = request.POST.get('office_hours', user.office_hours)
        office_location = request.POST.get('office_location', user.office_location)

        # Call the service function to update the user profile
        update_user_profile(request, user, name, home_address, phone_number, password, office_hours, office_location)

        messages.success(request, "Your profile has been updated successfully!")
        return redirect('edit_profile')

    return render(request, 'common/edit_profile.html', {'user': user})

@login_required
def view_ta_assignments(request):
    ta_users = MyUser.objects.filter(role='TA')
    context = {'ta_users': ta_users}
    return render(request, 'common/view_ta_assignments.html', context)

@login_required
def view_public_contacts(request):
    public_contacts = MyUser.objects.values('name', 'email', 'phone_number', 'office_hours', 'office_location')
    context = {'public_contacts': public_contacts}
    return render(request, 'common/view_public_contacts.html', context)

def course_assignment(request):
    courses = MyCourse.objects.prefetch_related('tas').select_related('instructor')
    instructors = MyUser.objects.filter(role='Instructor')
    tas = MyUser.objects.filter(role='TA')

    if request.method == 'POST':
        form = CourseAssignmentForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            instructor = form.cleaned_data['instructor']
            tas = form.cleaned_data['tas']

            course.instructor = instructor
            course.tas.set(tas)
            course.save()

            messages.success(request, 'Course assignment updated successfully!')
            return redirect('course_assignment')
    else:
        form = CourseAssignmentForm()

    return render(
        request,
        'admin/course_assignment.html',
        {
            'form': form,
            'courses': courses,
            'instructors': instructors,
            'tas': tas,
        }
    )
class CreateLabSectionView(LoginRequiredMixin, View):
    @method_decorator(role_required(allowed_roles=['Administrator', 'Instructor']))
    def get(self, request):
        form = LabSectionForm()
        return render(request, 'admin/create_lab_section.html', {'form': form})

    @method_decorator(role_required(allowed_roles=['Administrator', 'Instructor']))
    def post(self, request):
        form = LabSectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lab section created successfully!")
            return redirect('course_management')
        else:
            return render(request, 'admin/create_lab_section.html', {'form': form})