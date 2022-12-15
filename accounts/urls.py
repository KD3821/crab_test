from django.urls import path, include
from .views import show_users, login_view, logout_view, register_view

urlpatterns = [
    path('all/', show_users, name='all_users'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='reg'),
    path('register_ok/', register_view, name='reg_ok'),
]
