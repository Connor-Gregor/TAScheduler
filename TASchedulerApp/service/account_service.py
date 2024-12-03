from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

from TASchedulerApp.models import MyUser

class AccountService:
    @staticmethod
    def create_account(name, email, role, password):
        # Create a new user with the provided name, email, and role
        user = MyUser.objects.create(
            name=name,
            email=email,
            role=role,
        )

        user.set_password(password)

        user.save()
        return user

    @staticmethod
    def edit_user(user_id, new_data):
        try:
            # Get the user by their unique ID
            user = MyUser.objects.get(id=user_id)

            # Update the user's fields if new data is provided
            if 'new_name' in new_data:
                user.name = new_data['new_name']
            if 'new_password' in new_data:
                user.set_password(new_data['new_password'])
            if 'new_contact_info' in new_data:
                user.contactInfo = new_data['new_contact_info']
            if 'new_role' in new_data:
                user.role = new_data['new_role']

            # Save the updated user details to the database
            user.save()
        except MyUser.DoesNotExist:
            raise ValueError("User not found.")


    @staticmethod
    def delete_user(user_id):
        user = MyUser.objects.get(id=user_id)
        user.delete()
