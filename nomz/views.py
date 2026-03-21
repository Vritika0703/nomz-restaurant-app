from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_http_methods, require_POST
from .forms import (
    UserRegisterForm,
    UserLoginForm,
    RestaurantProfileForm,
    RestaurantAvailabilityForm,
    RestaurantActivationForm,
    RestaurantPhotoForm,
    UserPreferenceForm,
)
from .models import Restaurant, RestaurantPhoto, RestaurantSearch, UserPreference


def landing_page(request):
    """
    Landing page - splash screen entry point for the application
    Shows "Nomz" with "Click to start" message
    Always shows splash screen regardless of authentication status
    """
    context = {
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'nomz/splash.html', context)


def home(request):
    """
    Home page view - displays different content based on authentication status.
    Restaurant users are redirected to their profile instead.
    """
    # If user is authenticated and is a restaurant, redirect to profile
    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        if request.user.userprofile.role == 'restaurant':
            return redirect('profile')
    
    context = {
        'title': 'Home',
    }
    return render(request, 'nomz/home.html', context)


def perform_dependency_health_checks() -> None:
    """
    Dependency checks for /health/.

    Kept as a function so tests can patch failure scenarios easily.
    """
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SELECT 1;")
        cursor.fetchone()


def health_check(request):
    """
    Lightweight health endpoint for ELB/EB health checks.
    Must return HTTP 200 quickly and without auth redirects.
    """
    # Best-effort dependency checks. Keep it fast and avoid expensive ORM work.
    try:
        perform_dependency_health_checks()
        return JsonResponse({"status": "ok"}, status=200)
    except Exception as exc:
        # Let monitoring middleware convert non-200 responses into alerts/audit logs.
        return JsonResponse({"status": "degraded", "error": str(exc)[:200]}, status=503)


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
        return redirect('profile')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}!')
            login(request, user)
            return redirect('profile')
    else:
        form = UserRegisterForm()
    
    context = {'form': form, 'title': 'Register'}
    return render(request, 'nomz/register.html', context)


@require_http_methods(["GET", "POST"])
@login_required(login_url='landing')
def dashboard(request):
    """
    Dashboard dynamically routes based on the database profile and includes user preferences.
    """
    # 1. Determine User Role
    if request.user.is_superuser or request.user.is_staff:
        role = 'admin'
    elif hasattr(request.user, 'userprofile'):
        role = request.user.userprofile.role
    else:
        role = 'diner'

    # 2. Safely Fetch Preferences
    # This ensures the dashboard doesn't crash if preferences aren't set yet
    try:
        preferences = request.user.preferences
    except UserPreference.DoesNotExist:
        preferences = None

    context = {
        'title': 'Dashboard',
        'user': request.user,
        'role': role,
        'preferences': preferences,  # Add this to context
    }
    
    if role == 'restaurant':
        # Get the restaurant profile for the restaurant owner
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        context['restaurant'] = restaurant
        return render(request, 'nomz/restaurant_dashboard.html', context)
    elif role == 'admin':
        return render(request, 'nomz/admin_dashboard.html', context)
    else:
        # This matches the user_dashboard.html where your taste profile code is
        return render(request, 'nomz/user_dashboard.html', context)


@login_required(login_url='landing')
@require_http_methods(["POST"])
def user_logout(request):
    """
    User logout view
    Logs out the user and redirects to login page
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('signin')


# ============================================================================
# RESTAURANT PROFILE MANAGEMENT VIEWS
# ============================================================================


def is_restaurant_owner(user):
    """Helper function to check if user is a restaurant owner"""
    return hasattr(user, 'userprofile') and user.userprofile.role == 'restaurant'


@login_required(login_url='landing')
@require_http_methods(["GET"])
def restaurant_profile(request):
    """
    Restaurant-only profile page used by tests and for convenience navigation.

    For restaurant owners, renders the same UI as the dashboard restaurant view.
    """
    if not is_restaurant_owner(request.user):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('profile')
    return dashboard(request)


@login_required(login_url='landing')
@require_http_methods(["GET", "POST"])
def create_restaurant_profile(request):
    """
    Create a new restaurant profile
    Only for restaurant owners without a profile yet
    """
    if not is_restaurant_owner(request.user):
        messages.error(request, 'You do not have permission to create a restaurant profile.')
        return redirect('profile')
    
    # Check if user already has a restaurant
    if Restaurant.objects.filter(owner=request.user).exists():
        messages.info(request, 'You already have a restaurant profile.')
        return redirect('profile')
    
    if request.method == 'POST':
        form = RestaurantProfileForm(request.POST)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.owner = request.user
            restaurant.save()
            messages.success(request, 'Restaurant profile created successfully!')
            return redirect('profile')
    else:
        form = RestaurantProfileForm()
    
    context = {
        'title': 'Create Restaurant Profile',
        'form': form,
        'is_create': True,
    }
    return render(request, 'nomz/restaurant_form.html', context)


@login_required(login_url='landing')
@require_http_methods(["GET", "POST"])
def edit_restaurant_profile(request):
    """
    Edit existing restaurant profile
    Handles updates to description, hours, cuisine, and price range
    """
    if not is_restaurant_owner(request.user):
        messages.error(request, 'You do not have permission to edit a restaurant profile.')
        return redirect('profile')
    
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    
    if request.method == 'POST':
        form = RestaurantProfileForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Restaurant profile updated successfully!')
            return redirect('profile')
    else:
        form = RestaurantProfileForm(instance=restaurant)
    
    context = {
        'title': 'Edit Restaurant Profile',
        'form': form,
        'restaurant': restaurant,
        'is_create': False,
    }
    return render(request, 'nomz/restaurant_form.html', context)


@login_required(login_url='landing')
@require_http_methods(["GET", "POST"])
def manage_availability(request):
    """
    Manage restaurant availability (temporary closure)
    """
    if not is_restaurant_owner(request.user):
        messages.error(request, 'You do not have permission to manage availability.')
        return redirect('profile')
    
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    
    if request.method == 'POST':
        form = RestaurantAvailabilityForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            if restaurant.is_temporarily_unavailable:
                messages.success(request, 'Restaurant marked as temporarily unavailable.')
            else:
                messages.success(request, 'Restaurant availability updated.')
            return redirect('profile')
    else:
        form = RestaurantAvailabilityForm(instance=restaurant)
    
    context = {
        'title': 'Manage Availability',
        'form': form,
        'restaurant': restaurant,
    }
    return render(request, 'nomz/manage_availability.html', context)


@login_required(login_url='landing')
@require_http_methods(["GET", "POST"])
def manage_activation(request):
    """
    Activate or deactivate restaurant profile
    """
    if not is_restaurant_owner(request.user):
        messages.error(request, 'You do not have permission to manage activation.')
        return redirect('profile')
    
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    
    if request.method == 'POST':
        form = RestaurantActivationForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            if restaurant.is_active:
                messages.success(request, 'Restaurant profile is now visible to customers.')
            else:
                messages.warning(request, 'Restaurant profile has been deactivated. It is no longer visible to customers.')
            return redirect('profile')
    else:
        form = RestaurantActivationForm(instance=restaurant)
    
    context = {
        'title': 'Manage Profile Status',
        'form': form,
        'restaurant': restaurant,
    }
    return render(request, 'nomz/manage_activation.html', context)


@login_required(login_url='landing')
@require_http_methods(["GET", "POST"])
def upload_photo(request):
    """
    Upload a new restaurant photo
    """
    if not is_restaurant_owner(request.user):
        messages.error(request, 'You do not have permission to upload photos.')
        return redirect('profile')
    
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    
    if request.method == 'POST':
        form = RestaurantPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.restaurant = restaurant
            photo.save()
            messages.success(request, 'Photo uploaded successfully!')
            return redirect('restaurant_photos')
    else:
        form = RestaurantPhotoForm()
    
    context = {
        'title': 'Upload Photo',
        'form': form,
        'restaurant': restaurant,
    }
    return render(request, 'nomz/upload_photo.html', context)


@login_required(login_url='landing')
def restaurant_photos(request):
    """
    View and manage all restaurant photos
    """
    if not is_restaurant_owner(request.user):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('profile')
    
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    photos = restaurant.photos.all()
    
    context = {
        'title': 'Manage Photos',
        'restaurant': restaurant,
        'photos': photos,
    }
    return render(request, 'nomz/restaurant_photos.html', context)


@login_required(login_url='landing')
@require_POST
def delete_photo(request, photo_id):
    """
    Delete a restaurant photo
    """
    if not is_restaurant_owner(request.user):
        return HttpResponseForbidden('Permission denied')
    
    photo = get_object_or_404(RestaurantPhoto, id=photo_id)
    
    if photo.restaurant.owner != request.user:
        return HttpResponseForbidden('Permission denied')
    
    photo.delete()
    messages.success(request, 'Photo deleted successfully!')
    return redirect('restaurant_photos')


@login_required(login_url='landing')
@require_POST
def set_primary_photo(request, photo_id):
    """
    Set a photo as the primary (main) photo for the restaurant
    """
    if not is_restaurant_owner(request.user):
        return HttpResponseForbidden('Permission denied')
    
    photo = get_object_or_404(RestaurantPhoto, id=photo_id)
    
    if photo.restaurant.owner != request.user:
        return HttpResponseForbidden('Permission denied')
    
    # Set this as primary (the save method will handle unsetting others)
    photo.is_primary = True
    photo.save()
    messages.success(request, 'Primary photo updated!')
    return redirect('restaurant_photos')
@login_required(login_url='login')
def restaurant_search(request):
    query = request.GET.get('q', '')
    neighborhood = request.GET.get('neighborhood', '')

    # Primary search index
    results = RestaurantSearch.objects.all()
    if query:
        results = results.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(cuisine__icontains=query)
        )
    if neighborhood:
        results = results.filter(neighborhood__iexact=neighborhood)

    all_neighborhoods = RestaurantSearch.objects.values_list('neighborhood', flat=True).distinct()

    # Fallback path: if the search index is empty, read directly from Restaurant.
    if not RestaurantSearch.objects.exists():
        base_restaurants = Restaurant.objects.filter(is_active=True)
        if query:
            base_restaurants = base_restaurants.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(cuisine__icontains=query)
                | Q(cuisine_type__icontains=query)
                | Q(cuisine_tags__icontains=query)
            )
        if neighborhood:
            base_restaurants = base_restaurants.filter(
                Q(neighborhood__iexact=neighborhood) | Q(borough__iexact=neighborhood)
            )

        mapped_results = []
        for restaurant in base_restaurants.order_by('name'):
            fallback_cuisine = restaurant.cuisine or restaurant.cuisine_type or ''
            if not fallback_cuisine and restaurant.cuisine_tags:
                fallback_cuisine = ', '.join(str(tag) for tag in restaurant.cuisine_tags[:3])
            mapped_results.append(
                {
                    'name': restaurant.name,
                    'description': restaurant.description or '',
                    'cuisine': fallback_cuisine,
                    'neighborhood': restaurant.neighborhood or restaurant.borough or '',
                }
            )

        results = mapped_results
        all_neighborhoods = sorted(
            {
                restaurant.neighborhood or restaurant.borough
                for restaurant in Restaurant.objects.filter(is_active=True)
                if (restaurant.neighborhood or restaurant.borough)
            }
        )

    return render(request, 'nomz/search_results.html', {
        'results': results,
        'query': query,
        'neighborhood': neighborhood,
        'all_neighborhoods': all_neighborhoods
    })

# Add this to views.py

@login_required(login_url='landing')
def manage_preferences(request):
    """
    Create or Update user taste preferences
    """
    # Get or create the preference object for the current user
    preferences, created = UserPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your dining preferences have been updated!')
            return redirect('dashboard')
    else:
        form = UserPreferenceForm(instance=preferences)
    
    return render(request, 'nomz/manage_preferences.html', {
        'form': form,
        'title': 'My Preferences'
    })
