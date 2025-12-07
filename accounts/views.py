from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages

def register(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        if not all([username, email, password1, password2]):
            messages.error(request, 'All fields are required.')
            return render(request, 'accounts/register.html')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'accounts/register.html')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('login')
    
    return render(request, 'accounts/register.html')


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('finflow:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('finflow:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'accounts/login.html')
    
    return render(request, 'accounts/login.html')


@login_required
@require_http_methods(["POST"])
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

