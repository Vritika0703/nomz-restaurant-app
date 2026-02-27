from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import UserRegisterForm, UserLoginForm


def landing_page(request):
    """
    Landing page - entry point for the application
    Shows Sign Up and Login options
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    context = {
        'title': 'Welcome to Nomz',
    }
    return render(request, 'nomz/landing.html', context)


def role_selection(request):
    """
    Role selection page - allows users to choose between Restaurant and User roles
    Accessed from both signup and login flows
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Get the flow type (signup or login) from query parameter
    flow = request.GET.get('flow', 'signup')  # default to signup
    
    context = {
        'title': 'Choose Your Role',
        'flow': flow,
    }
    return render(request, 'nomz/role_selection.html', context)


def home(request):
    """
    Home page view - displays different content based on authentication status
    """
    context = {
        'title': 'Home',
    }
    return render(request, 'nomz/home.html', context)


@require_http_methods(["GET", "POST"])
def register(request, role=None):
    """
    User registration view
    Handles both GET (display form) and POST (process registration) requests
    Supports both 'user' and 'restaurant' roles
    Note: Admin accounts must be created by existing admins via the admin panel
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Admin accounts cannot be registered through this form
    if role == 'admin':
        messages.error(request, 'Admin accounts can only be created through the admin panel.')
        return redirect('landing')
    
    # Get role from URL parameter or form submission
    if role not in ['user', 'restaurant']:
        return redirect('landing')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Store role in session for later use
            request.session['user_role'] = role
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}!')
            login(request, user)
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegisterForm()
    
    context = {
        'form': form,
        'title': f'{role.capitalize()} Registration',
        'role': role,
    }
    return render(request, 'nomz/register.html', context)
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Store role in session for later use
            request.session['user_role'] = role
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}!')
            login(request, user)
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegisterForm()
    
    context = {
        'form': form,
        'title': f'{role.capitalize()} Registration',
        'role': role,
    }
    return render(request, 'nomz/register.html', context)


@require_http_methods(["GET", "POST"])
def user_login(request, role=None):
    """
    User login view
    Handles both GET (display form) and POST (process login) requests
    Supports 'user', 'restaurant', and 'admin' roles
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Get role from URL parameter or redirect to landing
    if role not in ['user', 'restaurant', 'admin']:
        return redirect('landing')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Validate admin login - user must be staff
                if role == 'admin' and not user.is_staff:
                    messages.error(request, 'Admin access denied. User does not have admin privileges.')
                else:
                    # Store role in session
                    request.session['user_role'] = role
                    login(request, user)
                    messages.success(request, f'Welcome back, {username}!')
                    next_url = request.GET.get('next', 'dashboard')
                    return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'title': f'{role.capitalize()} Login',
        'role': role,
    }
    return render(request, 'nomz/login.html', context)
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Validate admin login - user must be staff
                if role == 'admin' and not user.is_staff:
                    messages.error(request, 'Admin access denied. User does not have admin privileges.')
                else:
                    # Store role in session
                    request.session['user_role'] = role
                    login(request, user)
                    messages.success(request, f'Welcome back, {username}!')
                    next_url = request.GET.get('next', 'dashboard')
                    return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'title': f'{role.capitalize()} Login',
        'role': role,
    }
    return render(request, 'nomz/login.html', context)


@login_required(login_url='landing')
@require_http_methods(["POST"])
def user_logout(request):
    """
    User logout view
    Logs out the user and redirects to landing page
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('landing')


@login_required(login_url='landing')
def dashboard(request):
    """
    User dashboard view - requires authentication
    Displays user-specific or restaurant-specific information based on role
    """
    role = request.session.get('user_role', 'user')
    
    context = {
        'title': 'Dashboard',
        'user': request.user,
        'role': role,
    }
    
    # Render different templates based on role
    if role == 'restaurant':
        return render(request, 'nomz/restaurant_dashboard.html', context)
    elif role == 'admin':
        return render(request, 'nomz/admin_dashboard.html', context)
    else:
        return render(request, 'nomz/user_dashboard.html', context)
