"""
URL configuration for TAScheduler project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path

from TASchedulerApp import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication URLs
    path('', views.Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.Register.as_view(), name='register'),

    # Dashboard
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    # Common URLs (accessible by all roles)
    path('profile/', views.ProfileView.as_view(), name='profile'),
    #path('notifications/', views.NotificationsView.as_view(), name='notifications'),

    # Administrator URLs
    path('admin/create_course/', views.CreateCourseView.as_view(), name='create_course'),
    #path('admin/create_account/', views.CreateAccountView.as_view(), name='create_account'),
    #path('admin/delete_account/', views.DeleteAccountView.as_view(), name='delete_account'),
    #path('admin/edit_account/', views.EditAccountView.as_view(), name='edit_account'),
    #path('admin/assign_instructors/', views.AssignInstructorsView.as_view(), name='assign_instructors'),
    #path('admin/assign_tas/', views.AssignTAsView.as_view(), name='assign_tas'),
    #path('admin/assign_ta_labs/', views.AssignTALabsAdminView.as_view(), name='assign_ta_labs_admin'),
    #path('admin/send_notifications/', views.SendNotificationsView.as_view(), name='send_notifications_admin'),

    # Instructor URLs
    #path('instructor/view_course_assignments/', views.ViewCourseAssignmentsView.as_view(),name='view_course_assignments'),
    #path('instructor/view_ta_assignments/', views.ViewTAAssignmentsInstructorView.as_view(),name='view_ta_assignments_instructor'),
    #path('instructor/assign_ta_labs/', views.AssignTALabsInstructorView.as_view(), name='assign_ta_labs_instructor'),
    #path('instructor/contact_tas/', views.ContactTAsView.as_view(), name='contact_tas'),
    #path('instructor/send_notifications/', views.SendNotificationsView.as_view(), name='send_notifications_instructor'),

    # TA URLs
    #path('ta/edit_contact_info/', views.EditContactInfoView.as_view(), name='edit_contact_info'),
    #path('ta/view_ta_assignments/', views.ViewTAAssignmentsTAView.as_view(), name='view_ta_assignments_ta'),
    #path('ta/view_public_contacts/', views.ViewPublicContactsView.as_view(), name='view_public_contacts'),

]
