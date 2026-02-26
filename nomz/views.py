from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import UserRegisterForm, UserLoginForm


def home(request):
    """
    Home page view - displays different content based on authentication status
    """
    context = {
        'title': 'Home',
    }
    return render(request, 'nomz/home.html', context)


@require_http_methods(["GET", "POST"])
def register(request):
    """
    User registration view
    Handles both GET (display form) and POST (process registration) requests
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}!')
            login(request, user)
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegisterForm()
    
    context = {
        'form': form,
        'title': 'Register',
    }
    return render(request, 'nomz/register.html', context)


@require_http_methods(["GET", "POST"])
def user_login(request):
    """
    User login view
    Handles both GET (display form) and POST (process login) requests
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'title': 'Login',
    }
    return render(request, 'nomz/login.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def user_logout(request):
    """
    User logout view
    Logs out the user and redirects to login page
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    """
    User dashboard view - requires authentication
    Displays user-specific information
    """
    context = {
        'title': 'Dashboard',
        'user': request.user,
    }
    return render(request, 'nomz/dashboard.html', context)
