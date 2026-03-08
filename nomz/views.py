from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .forms import UserRegisterForm, UserLoginForm
from .models import Restaurant
from django.db.models import Q


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


def home(request):
    """
    Home page view - displays different content based on authentication status
    """
    context = {
        'title': 'Home',
    }
    return render(request, 'nomz/home.html', context)


def map_view(request):
    """
    Render interactive restaurant map page with filters and server-provided options.
    """
    restaurants = Restaurant.objects.filter(
        is_active=True,
        latitude__isnull=False,
        longitude__isnull=False,
    )
    boroughs = sorted(
        {
            borough.strip().title()
            for borough in restaurants.values_list("borough", flat=True)
            if borough
        }
    )

    search = request.GET.get("search", "").strip()
    borough = request.GET.get("borough", "").strip()
    min_score = request.GET.get("min_score", "").strip()
    max_score = request.GET.get("max_score", "").strip()
    cuisine = request.GET.get("cuisine", "").strip()
    sort_by = request.GET.get("sort_by", "score_desc").strip()

    if search:
        restaurants = restaurants.filter(
            Q(name__icontains=search)
            | Q(street__icontains=search)
            | Q(zip_code__icontains=search)
            | Q(borough__icontains=search)
        )
    if borough:
        restaurants = restaurants.filter(borough__iexact=borough)
    if cuisine:
        restaurants = restaurants.filter(cuisine_tags__icontains=cuisine)
    if min_score:
        try:
            restaurants = restaurants.filter(composite_score__gte=float(min_score))
        except ValueError:
            min_score = ""
    if max_score:
        try:
            restaurants = restaurants.filter(composite_score__lte=float(max_score))
        except ValueError:
            max_score = ""

    cuisines = set()
    for row in restaurants.values_list("cuisine_tags", flat=True):
        for value in row or []:
            cuisines.add(str(value).strip())

    context = {
        "title": "Restaurant Map",
        "search": search,
        "borough": borough,
        "min_score": min_score,
        "max_score": max_score,
        "cuisine": cuisine,
        "sort_by": sort_by,
        "boroughs": boroughs,
        "cuisines": sorted(filter(None, (item.title() for item in cuisines))),
        "restaurant_count": restaurants.count(),
    }
    return render(request, "nomz/map.html", context)


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}!')
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    
    context = {'form': form, 'title': 'Register'}
    return render(request, 'nomz/register.html', context)


@require_http_methods(["GET", "POST"])
def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
    else:
        form = UserLoginForm()
    
    context = {'form': form, 'title': 'Login'}
    return render(request, 'nomz/login.html', context)


@login_required(login_url='landing')
def dashboard(request):
    """
    Dashboard dynamically routes based on the database profile
    """
    # 1. Check if they are a built-in Django Admin
    if request.user.is_superuser or request.user.is_staff:
        role = 'admin'
    # 2. Check their profile in the database
    elif hasattr(request.user, 'userprofile'):
        role = request.user.userprofile.role
    # 3. Fallback
    else:
        role = 'diner' 

    context = {
        'title': 'Dashboard',
        'user': request.user,
        'role': role,
    }
    
    if role == 'restaurant':
        return render(request, 'nomz/restaurant_dashboard.html', context)
    elif role == 'admin':
        return render(request, 'nomz/admin_dashboard.html', context)
    else:
        return render(request, 'nomz/user_dashboard.html', context)


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

@login_required(login_url='login')
def restaurant_search(request):
    query = request.GET.get('q', '')
    neighborhood = request.GET.get('neighborhood', '')
    
    # Start with all restaurants
    results = Restaurant.objects.all()
    
    # Apply keyword search (Name or Description)
    if query:
        results = results.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(cuisine__icontains=query)
        )
    
    # Apply neighborhood filter
    if neighborhood:
        results = results.filter(neighborhood__iexact=neighborhood)
        
    # Get unique neighborhoods for the dropdown filter
    all_neighborhoods = Restaurant.objects.values_list('neighborhood', flat=True).distinct()

    return render(request, 'nomz/search_results.html', {
        'results': results,
        'query': query,
        'neighborhood': neighborhood,
        'all_neighborhoods': all_neighborhoods
    })
