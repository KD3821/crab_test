from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User
from .forms import UserLoginForm, UserRegisterForm

def show_users(request):
    users = User.objects.all()
    return render(request, 'users.html', {'users': users})


def login_view(request):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        data = form.cleaned_data
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)
        login(request, user)
        return redirect('quiz:all_topics')
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def register_view(request):
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data['password'])
        new_user.save()
        messages.success(request, "Вы успешно зарегистрированы")
        return render(request, 'register_done.html', {'new_user': new_user})
    return render(request, 'register.html', {'form': form})
