from django.shortcuts import render, redirect
from django.views import View

# Create your views here.
class Login(View):
    def get(self,request):
        return render(request,"login.html")

    def post(self, request):
        name = request.POST['name']
        password = request.POST['password']

        # Check if username exists
        #Change MyUser to name of class from models.py + include from .models import MyUser at the top
        try:
            user = MyUser.objects.get(name=name)
            if user.password == password:  # Check if the password matches
                request.session["name"] = user.name
                return redirect("/dashboard/")  # Redirect to /dashboard/ on success
            else:
                # Incorrect password
                return render(request, "login.html", {"message": "Incorrect password"})
        except MyUser.DoesNotExist:
            # Username does not exist
            return render(request, "login.html", {"message": "User does not exist"})

class Dashboard(View):
    def get(self,request):
        return render(request,"dashboard.html")