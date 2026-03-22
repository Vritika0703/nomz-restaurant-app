from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from nomz.ingestion.utils.score import compute_composite_score_from_records
from .filtering import (
    DIETARY_OPTIONS,
    parse_bool,
    apply_open_now_filter,
    apply_restaurant_filters,
    restaurant_ordering,
)
from .forms import (
    AdminLoginForm,
    UserRegisterForm,
    RestaurantProfileForm,
    RestaurantOwnershipClaimForm,
    RestaurantAvailabilityForm,
    RestaurantActivationForm,
    RestaurantPhotoForm,
    UserPreferenceForm,
)
from .models import (
    LoginLog,
    Restaurant,
    RestaurantOwnershipClaim,
    RestaurantPhoto,
    UserPreference,
    UserProfile,
)


def _to_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _build_restaurant_score_insights(restaurant):
    latest_inspection = restaurant.inspections.order_by(
        "-inspection_date", "-id"
    ).first()
    if latest_inspection is not None:
        latest_score_data = compute_composite_score_from_records([latest_inspection])
    else:
        latest_score_data = {
            "composite_score": None,
            "grade": "",
            "grade_score": None,
            "violation_score": 0.0,
            "recency_score": 0.0,
            "last_inspection_date": None,
            "critical_violations": 0,
            "noncritical_violations": 0,
        }

    composite_score_value = (
        _to_float(restaurant.composite_score)
        if restaurant.composite_score is not None
        else _to_float(latest_score_data.get("composite_score"))
    )
    grade_score_value = (
        int(restaurant.grade_score_latest)
        if restaurant.grade_score_latest is not None
        else int(latest_score_data.get("grade_score") or 0)
    )
    grade_value = (
        restaurant.grade_latest or latest_score_data.get("grade") or ""
    ).strip()
    last_inspection_date_value = (
        restaurant.last_inspection_date or latest_score_data.get("last_inspection_date")
    )

    violation_score = float(latest_score_data.get("violation_score") or 0.0)
    recency_score = float(latest_score_data.get("recency_score") or 0.0)
    critical_violations = int(latest_score_data.get("critical_violations") or 0)
    noncritical_violations = int(latest_score_data.get("noncritical_violations") or 0)

    score_summary = {
        "composite_score": composite_score_value,
        "grade": grade_value or "N/A",
        "grade_score": grade_score_value,
        "last_inspection_date": last_inspection_date_value,
    }

    score_breakdown = [
        {
            "label": "Grade Quality",
            "raw_value": grade_score_value,
            "weight_percent": 50,
            "weighted_contribution": round(grade_score_value * 0.50, 2),
            "description": f"Latest grade: {grade_value or 'Not graded'}",
        },
        {
            "label": "Violation Profile",
            "raw_value": round(violation_score, 2),
            "weight_percent": 35,
            "weighted_contribution": round(violation_score * 0.35, 2),
            "description": (
                f"Critical: {critical_violations}, Non-critical: {noncritical_violations}"
            ),
        },
        {
            "label": "Inspection Recency",
            "raw_value": round(recency_score, 2),
            "weight_percent": 15,
            "weighted_contribution": round(recency_score * 0.15, 2),
            "description": (
                f"Last inspected: {last_inspection_date_value}"
                if last_inspection_date_value
                else "No inspection date available"
            ),
        },
    ]

    trend_rows = list(restaurant.inspections.order_by("-inspection_date", "-id")[:8])
    trend_rows.reverse()
    trend_points = []
    for inspection in trend_rows:
        point_score = compute_composite_score_from_records([inspection])
        trend_points.append(
            {
                "date": inspection.inspection_date.isoformat(),
                "label": inspection.inspection_date.strftime("%b %d, %Y"),
                "composite_score": _to_float(point_score.get("composite_score")) or 0.0,
                "grade": (inspection.grade or "").strip().upper() or "N/A",
                "grade_score": int(point_score.get("grade_score") or 0),
                "critical_violations": int(inspection.critical_violations or 0),
                "noncritical_violations": int(inspection.noncritical_violations or 0),
                "inspection_type": inspection.inspection_type or "",
            }
        )

    trend_summary = {
        "direction": "flat",
        "delta": 0.0,
        "has_data": bool(trend_points),
    }
    if len(trend_points) >= 2:
        delta = round(
            trend_points[-1]["composite_score"] - trend_points[0]["composite_score"], 2
        )
        trend_summary["delta"] = delta
        if delta > 1:
            trend_summary["direction"] = "up"
        elif delta < -1:
            trend_summary["direction"] = "down"

    location_scope = ""
    peers = Restaurant.objects.filter(is_active=True, composite_score__isnull=False)
    if restaurant.neighborhood:
        peers = peers.filter(neighborhood__iexact=restaurant.neighborhood)
        location_scope = restaurant.neighborhood
    elif restaurant.borough:
        peers = peers.filter(borough__iexact=restaurant.borough)
        location_scope = restaurant.borough
    elif restaurant.zip_code:
        peers = peers.filter(zip_code__startswith=(restaurant.zip_code or "")[:5])
        location_scope = (restaurant.zip_code or "")[:5]
    else:
        location_scope = "citywide"

    peer_rows = list(peers.values("id", "composite_score"))
    peer_count = len(peer_rows)
    neighborhood_comparison = {
        "location_scope": location_scope,
        "peer_count": peer_count,
        "rank": None,
        "percentile": None,
        "average_score": None,
        "delta_vs_average": None,
    }

    if composite_score_value is not None and peer_count > 0:
        sorted_rows = sorted(
            peer_rows,
            key=lambda item: float(item["composite_score"]),
            reverse=True,
        )
        restaurant_rank = next(
            (
                index + 1
                for index, item in enumerate(sorted_rows)
                if item["id"] == restaurant.id
            ),
            None,
        )
        if restaurant_rank is None:
            restaurant_rank = (
                sum(
                    1
                    for item in sorted_rows
                    if float(item["composite_score"]) > composite_score_value
                )
                + 1
            )

        average_score = round(
            sum(float(item["composite_score"]) for item in peer_rows) / peer_count,
            2,
        )
        percentile = round(((peer_count - restaurant_rank + 1) / peer_count) * 100, 1)
        neighborhood_comparison.update(
            {
                "rank": restaurant_rank,
                "percentile": percentile,
                "average_score": average_score,
                "delta_vs_average": round(composite_score_value - average_score, 2),
            }
        )

    return {
        "score_summary": score_summary,
        "score_breakdown": score_breakdown,
        "trend_points": trend_points,
        "trend_summary": trend_summary,
        "neighborhood_comparison": neighborhood_comparison,
    }


def landing_page(request):
    """
    Landing page - splash screen entry point for the application
    Shows "Nomz" with "Click to start" message
    Always shows splash screen regardless of authentication status
    """
    context = {
        "is_authenticated": request.user.is_authenticated,
    }
    return render(request, "nomz/splash.html", context)


def home(request):
    """
    Home page view - displays different content based on authentication status.
    Restaurant users are redirected to their profile instead.
    """
    # If user is authenticated and is a restaurant, redirect to profile
    if request.user.is_authenticated and hasattr(request.user, "userprofile"):
        if request.user.userprofile.role == "restaurant":
            return redirect("profile")

    context = {
        "title": "Home",
    }
    return render(request, "nomz/home.html", context)


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
    try:
        perform_dependency_health_checks()
        return JsonResponse({"status": "ok"}, status=200)
    except Exception as exc:
        return JsonResponse({"status": "degraded", "error": str(exc)[:200]}, status=503)


def map_view(request):
    """
    Render interactive restaurant map page with filters and server-provided options.
    """
    restaurants = apply_restaurant_filters(
        Restaurant.objects.all(),
        params=request.GET,
        require_coordinates=True,
    )
    boroughs = sorted(
        {
            borough.strip().title()
            for borough in Restaurant.objects.filter(
                is_active=True, latitude__isnull=False, longitude__isnull=False
            ).values_list("borough", flat=True)
            if borough
        }
    )

    search = request.GET.get("search", "").strip()
    borough = request.GET.get("borough", "").strip()
    cuisine = request.GET.get("cuisine", "").strip()
    min_score = request.GET.get("min_score", "").strip()
    max_score = request.GET.get("max_score", "").strip()
    price_range = request.GET.get("price_range", "").strip()
    min_rating = request.GET.get("min_rating", "").strip()
    dietary = request.GET.getlist("dietary") if hasattr(request, "GET") else []
    sort_by = request.GET.get("sort_by", "score_desc").strip()
    open_now = parse_bool(request.GET.get("open_now"))

    if open_now:
        ordered = restaurants.order_by(*restaurant_ordering(sort_by))[:2000]
        restaurant_count = len(apply_open_now_filter(ordered))
    else:
        restaurant_count = restaurants.count()

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
        "price_range": price_range,
        "min_rating": min_rating,
        "dietary": [item.lower() for item in dietary if item],
        "open_now": open_now,
        "sort_by": sort_by,
        "boroughs": boroughs,
        "cuisines": sorted(filter(None, (item.title() for item in cuisines))),
        "price_ranges": Restaurant.PRICE_CHOICES,
        "dietary_options": DIETARY_OPTIONS,
        "restaurant_count": restaurant_count,
    }
    return render(request, "nomz/map.html", context)


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            role = form.cleaned_data.get("role")
            messages.success(request, f"Account created successfully for {username}!")
            login(request, user)
            if role == "restaurant":
                messages.info(
                    request,
                    "Claim your restaurant listing to unlock owner controls.",
                )
                return redirect("claim_restaurant")
            return redirect("profile")
    else:
        form = UserRegisterForm()

    context = {"form": form, "title": "Register"}
    return render(request, "nomz/register.html", context)


@require_http_methods(["GET", "POST"])
def admin_login(request):
    """
    Secure login for administrators only.
    Requires a specialized form with a security code.
    """
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect("dashboard")
        logout(request)

    if request.method == "POST":
        form = AdminLoginForm(request, data=request.POST)
        username = request.POST.get("username")

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Admin session established for {username}.")
            return redirect("dashboard")
    else:
        form = AdminLoginForm()

    context = {"form": form, "title": "Secure Admin Login"}
    return render(request, "nomz/admin_login.html", context)


@staff_member_required
def admin_login_logs(request):
    logs = LoginLog.objects.all().order_by("-timestamp")
    context = {"title": "Login Activity Monitoring", "logs": logs}
    return render(request, "nomz/admin_logs.html", context)


@staff_member_required
def admin_manage_users(request):
    users = User.objects.all().exclude(pk=request.user.pk).order_by("-date_joined")

    from django.db.models import Exists, OuterRef

    suspicious_logs = LoginLog.objects.filter(
        username=OuterRef("username"), is_user_suspicious=True
    )
    users = users.annotate(has_suspicious_activity=Exists(suspicious_logs))

    context = {"title": "User Management", "users": users}
    return render(request, "nomz/admin_manage_users.html", context)


@staff_member_required
@require_POST
def toggle_user_status(request, user_id):
    user_to_toggle = get_object_or_404(User, id=user_id)
    if user_to_toggle.is_superuser:
        messages.error(request, "Cannot toggle status of superusers.")
    else:
        user_to_toggle.is_active = not user_to_toggle.is_active
        user_to_toggle.save()
        status_msg = "restored" if user_to_toggle.is_active else "revoked"
        messages.success(
            request, f"Access for {user_to_toggle.username} has been {status_msg}."
        )

    return redirect("admin_manage_users")


@require_http_methods(["GET", "POST"])
@login_required(login_url="landing")
def dashboard(request):
    """
    Dashboard dynamically routes based on the database profile and includes user preferences.
    """
    # 1. Determine User Role
    if request.user.is_superuser or request.user.is_staff:
        role = "admin"
    elif hasattr(request.user, "userprofile"):
        role = request.user.userprofile.role
    else:
        role = "diner"

    # 2. Safely Fetch Preferences
    # This ensures the dashboard doesn't crash if preferences aren't set yet
    try:
        preferences = request.user.preferences
    except UserPreference.DoesNotExist:
        preferences = None

    context = {
        "title": "Dashboard",
        "user": request.user,
        "role": role,
        "preferences": preferences,  # Add this to context
    }

    if role == "restaurant":
        # Get the restaurant profile for the restaurant owner
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        active_claim = (
            RestaurantOwnershipClaim.objects.filter(
                claimant=request.user,
                status=RestaurantOwnershipClaim.STATUS_PENDING,
            )
            .select_related("restaurant")
            .first()
        )
        recent_claims = RestaurantOwnershipClaim.objects.filter(
            claimant=request.user,
        ).select_related("restaurant")[:5]
        context["restaurant"] = restaurant
        context["active_claim"] = active_claim
        context["recent_claims"] = recent_claims
        if restaurant is not None:
            context.update(_build_restaurant_score_insights(restaurant))
        return render(request, "nomz/restaurant_dashboard.html", context)
    elif role == "admin":
        all_users = (
            User.objects.all().select_related("userprofile").order_by("-date_joined")
        )
        diner_count = UserProfile.objects.filter(role="diner").count()
        restaurant_count = Restaurant.objects.count()
        recent_logins = LoginLog.objects.all().order_by("-timestamp")[:10]
        suspicious_count = LoginLog.objects.filter(is_suspicious=True).count()

        context.update(
            {
                "all_users": all_users,
                "diner_count": diner_count,
                "restaurant_count": restaurant_count,
                "recent_logins": recent_logins,
                "suspicious_count": suspicious_count,
                "total_users": User.objects.count(),
            }
        )
        return render(request, "nomz/admin_dashboard.html", context)
    else:
        # This matches the user_dashboard.html where your taste profile code is
        return render(request, "nomz/user_dashboard.html", context)


@login_required(login_url="landing")
@require_http_methods(["POST"])
def user_logout(request):
    """
    User logout view
    Logs out the user and redirects to login page
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("signin")


# ============================================================================
# RESTAURANT PROFILE MANAGEMENT VIEWS
# ============================================================================


def is_restaurant_owner(user):
    """Helper function to check if user is a restaurant owner"""
    return hasattr(user, "userprofile") and user.userprofile.role == "restaurant"


@login_required(login_url="landing")
def restaurant_profile(request):
    """
    Legacy route for restaurant profile page.
    Restaurant owners can access; diners/admins are redirected.
    """
    if not is_restaurant_owner(request.user):
        return redirect("profile")

    restaurant = Restaurant.objects.filter(owner=request.user).first()
    context = {
        "title": "Restaurant Profile",
        "user": request.user,
        "role": "restaurant",
        "restaurant": restaurant,
        "active_claim": None,
        "recent_claims": [],
    }
    if restaurant is not None:
        context.update(_build_restaurant_score_insights(restaurant))
    return render(request, "nomz/restaurant_dashboard.html", context)


@login_required(login_url="landing")
@require_http_methods(["GET", "POST"])
def claim_restaurant(request):
    """
    Allow a restaurant-role user to claim ownership of an existing restaurant row.
    Claims are reviewed before assignment.
    """
    if not is_restaurant_owner(request.user):
        messages.error(
            request, "Only restaurant owner accounts can submit ownership claims."
        )
        return redirect("profile")

    if Restaurant.objects.filter(owner=request.user).exists():
        messages.info(
            request, "You already have a restaurant assigned to your account."
        )
        return redirect("profile")

    active_claim = (
        RestaurantOwnershipClaim.objects.filter(
            claimant=request.user,
            status=RestaurantOwnershipClaim.STATUS_PENDING,
        )
        .select_related("restaurant")
        .first()
    )

    search_query = (
        request.POST.get("search", "")
        if request.method == "POST"
        else request.GET.get("search", "")
    )
    form = RestaurantOwnershipClaimForm(
        request.POST or None,
        user=request.user,
        search_query=search_query,
    )

    if request.method == "POST" and active_claim:
        messages.warning(
            request,
            f'You already have a pending claim for "{active_claim.restaurant.name}". Please wait for review.',
        )
        return redirect("claim_restaurant")

    if request.method == "POST" and form.is_valid():
        claim = form.save()
        messages.success(
            request,
            f'Claim submitted for "{claim.restaurant.name}". We will review your verification details shortly.',
        )
        return redirect("profile")

    recent_claims = RestaurantOwnershipClaim.objects.filter(
        claimant=request.user,
    ).select_related("restaurant")[:5]

    context = {
        "title": "Claim Restaurant",
        "form": form,
        "search_query": search_query,
        "active_claim": active_claim,
        "recent_claims": recent_claims,
    }
    return render(request, "nomz/claim_restaurant.html", context)


@login_required(login_url="landing")
@require_http_methods(["GET", "POST"])
def create_restaurant_profile(request):
    """
    Create a new restaurant profile
    Only for restaurant owners without a profile yet
    """
    if not is_restaurant_owner(request.user):
        messages.error(
            request, "You do not have permission to create a restaurant profile."
        )
        return redirect("profile")

    # Check if user already has a restaurant
    if Restaurant.objects.filter(owner=request.user).exists():
        messages.info(request, "You already have a restaurant profile.")
        return redirect("profile")

    if request.method == "POST":
        form = RestaurantProfileForm(request.POST)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.owner = request.user
            restaurant.save()
            messages.success(request, "Restaurant profile created successfully!")
            return redirect("profile")
    else:
        form = RestaurantProfileForm()

    context = {
        "title": "Create Restaurant Profile",
        "form": form,
        "is_create": True,
    }
    return render(request, "nomz/restaurant_form.html", context)


@login_required(login_url="landing")
@require_http_methods(["GET", "POST"])
def edit_restaurant_profile(request):
    """
    Edit existing restaurant profile
    Handles updates to description, hours, cuisine, and price range
    """
    if not is_restaurant_owner(request.user):
        messages.error(
            request, "You do not have permission to edit a restaurant profile."
        )
        return redirect("profile")

    restaurant = get_object_or_404(Restaurant, owner=request.user)

    if request.method == "POST":
        form = RestaurantProfileForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, "Restaurant profile updated successfully!")
            return redirect("profile")
    else:
        form = RestaurantProfileForm(instance=restaurant)

    context = {
        "title": "Edit Restaurant Profile",
        "form": form,
        "restaurant": restaurant,
        "is_create": False,
    }
    return render(request, "nomz/restaurant_form.html", context)


@login_required(login_url="landing")
@require_http_methods(["GET", "POST"])
def manage_availability(request):
    """
    Manage restaurant availability (temporary closure)
    """
    if not is_restaurant_owner(request.user):
        messages.error(request, "You do not have permission to manage availability.")
        return redirect("profile")

    restaurant = get_object_or_404(Restaurant, owner=request.user)

    if request.method == "POST":
        form = RestaurantAvailabilityForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            if restaurant.is_temporarily_unavailable:
                messages.success(
                    request, "Restaurant marked as temporarily unavailable."
                )
            else:
                messages.success(request, "Restaurant availability updated.")
            return redirect("profile")
    else:
        form = RestaurantAvailabilityForm(instance=restaurant)

    context = {
        "title": "Manage Availability",
        "form": form,
        "restaurant": restaurant,
    }
    return render(request, "nomz/manage_availability.html", context)


@login_required(login_url="landing")
@require_http_methods(["GET", "POST"])
def manage_activation(request):
    """
    Activate or deactivate restaurant profile
    """
    if not is_restaurant_owner(request.user):
        messages.error(request, "You do not have permission to manage activation.")
        return redirect("profile")

    restaurant = get_object_or_404(Restaurant, owner=request.user)

    if request.method == "POST":
        form = RestaurantActivationForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            if restaurant.is_active:
                messages.success(
                    request, "Restaurant profile is now visible to customers."
                )
            else:
                messages.warning(
                    request,
                    "Restaurant profile has been deactivated. It is no longer visible to customers.",
                )
            return redirect("profile")
    else:
        form = RestaurantActivationForm(instance=restaurant)

    context = {
        "title": "Manage Profile Status",
        "form": form,
        "restaurant": restaurant,
    }
    return render(request, "nomz/manage_activation.html", context)


@login_required(login_url="landing")
@require_http_methods(["GET", "POST"])
def upload_photo(request):
    """
    Upload a new restaurant photo
    """
    if not is_restaurant_owner(request.user):
        messages.error(request, "You do not have permission to upload photos.")
        return redirect("profile")

    restaurant = get_object_or_404(Restaurant, owner=request.user)

    if request.method == "POST":
        form = RestaurantPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.restaurant = restaurant
            photo.save()
            messages.success(request, "Photo uploaded successfully!")
            return redirect("restaurant_photos")
    else:
        form = RestaurantPhotoForm()

    context = {
        "title": "Upload Photo",
        "form": form,
        "restaurant": restaurant,
    }
    return render(request, "nomz/upload_photo.html", context)


@login_required(login_url="landing")
def restaurant_photos(request):
    """
    View and manage all restaurant photos
    """
    if not is_restaurant_owner(request.user):
        messages.error(request, "You do not have permission to access this page.")
        return redirect("profile")

    restaurant = get_object_or_404(Restaurant, owner=request.user)
    photos = restaurant.photos.all()

    context = {
        "title": "Manage Photos",
        "restaurant": restaurant,
        "photos": photos,
    }
    return render(request, "nomz/restaurant_photos.html", context)


@login_required(login_url="landing")
@require_POST
def delete_photo(request, photo_id):
    """
    Delete a restaurant photo
    """
    if not is_restaurant_owner(request.user):
        return HttpResponseForbidden("Permission denied")

    photo = get_object_or_404(RestaurantPhoto, id=photo_id)

    if photo.restaurant.owner != request.user:
        return HttpResponseForbidden("Permission denied")

    photo.delete()
    messages.success(request, "Photo deleted successfully!")
    return redirect("restaurant_photos")


@login_required(login_url="landing")
@require_POST
def set_primary_photo(request, photo_id):
    """
    Set a photo as the primary (main) photo for the restaurant
    """
    if not is_restaurant_owner(request.user):
        return HttpResponseForbidden("Permission denied")

    photo = get_object_or_404(RestaurantPhoto, id=photo_id)

    if photo.restaurant.owner != request.user:
        return HttpResponseForbidden("Permission denied")

    # Set this as primary (the save method will handle unsetting others)
    photo.is_primary = True
    photo.save()
    messages.success(request, "Primary photo updated!")
    return redirect("restaurant_photos")


def restaurant_search(request):
    query = request.GET.get("q", "")
    neighborhood = request.GET.get("neighborhood", "")
    cuisine = request.GET.get("cuisine", "")
    price_range = request.GET.get("price_range", "")
    min_rating = request.GET.get("min_rating", "")
    min_composite = request.GET.get("min_composite_score", "")
    max_composite = request.GET.get("max_composite_score", "")
    dietary = request.GET.getlist("dietary") if hasattr(request, "GET") else []
    open_now = parse_bool(request.GET.get("open_now"))
    sort_by = request.GET.get("sort_by", "score_desc")

    results = apply_restaurant_filters(
        Restaurant.objects.filter(is_active=True),
        params=request.GET,
        require_coordinates=False,
    ).order_by(*restaurant_ordering(sort_by))

    if open_now:
        results = apply_open_now_filter(results)
    else:
        results = list(results)

    all_neighborhoods = sorted(
        {
            restaurant.neighborhood or restaurant.borough
            for restaurant in Restaurant.objects.filter(is_active=True)
            if (restaurant.neighborhood or restaurant.borough)
        }
    )

    cuisines = sorted(
        {
            (item or "").strip().title()
            for item in Restaurant.objects.values_list("cuisine", flat=True).filter(
                is_active=True
            )
            if item
        }
    )

    return render(
        request,
        "nomz/search_results.html",
        {
            "results": results,
            "query": query,
            "neighborhood": neighborhood,
            "all_neighborhoods": all_neighborhoods,
            "cuisines": cuisines,
            "all_price_ranges": Restaurant.PRICE_CHOICES,
            "dietary_values": [item.lower() for item in dietary if item],
            "dietary_options": DIETARY_OPTIONS,
            "min_rating": min_rating,
            "min_composite": min_composite,
            "max_composite": max_composite,
            "price_range": price_range,
            "cuisine_filter": cuisine,
            "open_now": open_now,
            "sort_by": sort_by,
            "count": len(results),
        },
    )


@login_required(login_url="landing")
def manage_preferences(request):
    """
    Create or Update user taste preferences
    """
    # Get or create the preference object for the current user
    preferences, created = UserPreference.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, "Your dining preferences have been updated!")
            return redirect("dashboard")
    else:
        form = UserPreferenceForm(instance=preferences)

    return render(
        request,
        "nomz/manage_preferences.html",
        {"form": form, "title": "My Preferences"},
    )


def admin_toggle_user_status(request, user_id):
    """
    Directly toggle user active status from the admin dashboard.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden(
            "You do not have permission to perform this action."
        )

    user_to_change = get_object_or_404(User, id=user_id)
    action = request.POST.get("action")

    if user_to_change == request.user:
        messages.error(request, "You cannot change your own status!")
    elif user_to_change.is_superuser and not request.user.is_superuser:
        messages.error(
            request, "You do not have permission to change a superuser status."
        )
    else:
        if action == "activate":
            user_to_change.is_active = True
            messages.success(
                request, f"Access ALLOWED for user: {user_to_change.username}"
            )
        elif action == "deactivate":
            user_to_change.is_active = False
            messages.success(
                request, f"Access REVOKED for user: {user_to_change.username}"
            )
        else:
            messages.error(request, "Invalid action.")

        user_to_change.save()

    return redirect("dashboard")
