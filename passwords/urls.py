from django.urls import path
from .views import login_view, password_list,delete_password

urlpatterns = [
    path('', login_view, name='login'),
    path('passwords/', password_list, name='password_list'),
    path('delete/<int:id>/', delete_password, name='delete_password'),
]
