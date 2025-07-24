from django.urls import path
from . import views

# urls.py
urlpatterns = [
    path('home', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('download/invoice/', views.download_invoice, name='download_invoice'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    path('', views.send_bulk_email, name='email_sender'),
]