from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import CourseForm, RegistrationForm
from django.utils.decorators import method_decorator
from .decorators import role_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import MyCourse, MyUser, Notification


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
        return render(request, 'admin/course_management.html')

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
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
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
        # Logic for fetching and displaying notifications
        return render(request, 'common/notifications.html')

@login_required
def manage_users(request):
    users = MyUser.objects.filter(role__in=['Instructor', 'TA'])
    return render(request, 'admin/manage_users.html', {'users': users})

@login_required
def edit_user(request, user_id):

    user = get_object_or_404(MyUser, id=user_id)

    if request.method == 'POST':
        new_name = request.POST.get('newName', None)
        new_password = request.POST.get('newPassword', None)
        new_contact_info = request.POST.get('newContactInfo', None)
        new_role = request.POST.get('newRole', None)

        if not (new_name or new_password or new_contact_info or new_role):
            return render(
                request,
                'admin/edit_user.html',
                {
                    'user': user,
                    'error': "At least one field (newName, newPassword, newContactInfo, New Role) must be provided.",
                },
            )

        if new_name:
            user.name = new_name
        if new_password:
            user.set_password(new_password)
        if new_contact_info:
            user.email = new_contact_info
        if new_role:
            user.role = new_role

        user.save()

        return redirect('account_management')

    return render(request, 'admin/edit_user.html', {'user': user})

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(MyUser, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('account_management')
    return render(request, 'admin/confirm_delete.html', {'user': user})

@login_required
def edit_course(request, course_id):

    course = get_object_or_404(MyCourse, id=course_id)

    if request.method == 'POST':
        new_name = request.POST.get('newName', None)
        new_instructor = request.POST.get('newInstructor', None)
        new_room = request.POST.get('newRoom', None)
        new_time = request.POST.get('newTime', None)

        if not (new_name or new_instructor or new_room or new_time):
            return render(
                request,
                'admin/edit_course.html',
                {
                    'course': course,
                    'error': "At least one field (newName, newInstructor, newRoom, NewTime) must be provided.",
                },
            )

        if new_name:
            course.name = new_name
        if new_instructor:
            course.instructor = new_instructor
        if new_room:
            course.room = new_room
        if new_time:
            course.time = new_time

        course.save()

        return redirect('course_management')

    return render(request, 'admin/edit_course.html', {'course': course})

def notifications(request):
    # Filter notifications where the logged-in user is the recipient
    notificationsList = Notification.objects.filter(recipient=request.user).order_by('-time_received')
    return render(request, 'common/notifications.html', {'notifications': notificationsList})


def send_notification(request):
    if request.method == "POST":
        title = request.POST.get('title')
        sender = request.user.name
        sender_email = request.user.email
        recipient_email = request.POST.get('recipient_email')

        # Validate recipient
        try:
            recipient = MyUser.objects.get(email=recipient_email)
        except MyUser.DoesNotExist:
            messages.error(request, "Invalid recipient email!")
            return redirect('send_notifications')

        # Create the notification
        notification = Notification.objects.create(
            title=title,
            sender=sender,
            recipient=recipient
        )

        # Send email to recipient

        return redirect('notifications')

    return render(request, 'instructor/send_notifications.html')