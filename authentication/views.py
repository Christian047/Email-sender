from django.shortcuts import render, redirect
from django.http import HttpResponse


# Hardcoded credentials
HARDCODED_USERNAME = "admin"
HARDCODED_PASSWORD = "12440"

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == HARDCODED_USERNAME and password == HARDCODED_PASSWORD:
            request.session["is_authenticated"] = True
            return redirect("email_sender")  # Change "home" to your main page view name
        else:
            return render(request, "mylogin.html", {"error": "Invalid credentials"})

    return render(request, "mylogin.html")

def home_view(request):
    if not request.session.get("is_authenticated"):
        return redirect("login")

    return redirect('email_sender')

