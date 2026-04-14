from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from datetime import timedelta
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q, Avg, Count
from django.db import models
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from nomz.ingestion.utils.score import compute_restaurant_composite_score
from nomz.scoring import SCORE_ALGORITHM_VERSION, refresh_restaurant_composite
from .forms import (
    UserRegisterForm,
    AdminLoginForm,
    RestaurantProfileForm,
    RestaurantOwnershipClaimForm,
    RestaurantAvailabilityForm,
    RestaurantActivationForm,
    RestaurantPhotoForm,
    UserPreferenceForm,
    ReviewForm,
    ReviewResponseForm,
    ModerationReportForm,
    RestaurantCommunicationSettingsForm,
)
from django.contrib.auth.models import User
from .models import (
    Conversation,
    CompositeScoreAnomaly,
    CompositeScoreHistory,
    Restaurant,
    RestaurantOwnershipClaim,
    RestaurantPhoto,
    Message,
    MessageNotification,
    UserPreference,
    UserProfile,
    LoginLog,
    Review,
    ReviewResponse,
    ModerationReport,
    SystemAuditLog,
    FriendMessage,
    FriendConversation,
    FriendSharedRestaurant,
)
from .restaurant_sorting import (
    normalize_sort_key,
    sort_restaurant_queryset,
    recommend_restaurants_for_user,
)

NYC_MIN_LAT = 40.0
NYC_MAX_LAT = 41.5
NYC_MIN_LON = -75.5
NYC_MAX_LON = -72.0


def _to_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _refresh_restaurant_composite_fields(restaurant):
    return refresh_restaurant_composite(restaurant)


def _build_restaurant_score_insights(restaurant):
    current_score_data = compute_restaurant_composite_score(restaurant)
    composite_score_value = (
        _to_float(restaurant.composite_score)
        if restaurant.composite_score is not None
        else _to_float(current_score_data.get("composite_score"))
    )
    grade_score_value = (
        int(restaurant.grade_score_latest)
        if restaurant.grade_score_latest is not None
        else int(current_score_data.get("grade_score") or 0)
    )
    grade_value = (
        restaurant.grade_latest or current_score_data.get("grade") or ""
    ).strip()
    last_inspection_date_value = (
        restaurant.last_inspection_date
        or current_score_data.get("last_inspection_date")
    )

    score_summary = {
        "composite_score": composite_score_value,
        "grade": grade_value or "N/A",
        "grade_score": grade_score_value,
        "last_inspection_date": last_inspection_date_value,
        "review_count": int(current_score_data.get("review_count") or 0),
        "review_confidence": round(
            float(current_score_data.get("review_confidence") or 0.0) * 100, 1
        ),
    }

    review_factor_averages = current_score_data.get("review_factor_averages", {})
    review_factor_scores = current_score_data.get("review_factor_scores", {})
    review_factor_breakdown = [
        {
            "label": "Overall",
            "average_rating": review_factor_averages.get("overall_rating"),
            "score_100": review_factor_scores.get("overall_rating", 0),
        },
        {
            "label": "Food Quality",
            "average_rating": review_factor_averages.get("food_quality_rating"),
            "score_100": review_factor_scores.get("food_quality_rating", 0),
        },
        {
            "label": "Service Quality",
            "average_rating": review_factor_averages.get("service_quality_rating"),
            "score_100": review_factor_scores.get("service_quality_rating", 0),
        },
        {
            "label": "Ambience",
            "average_rating": review_factor_averages.get("ambience_rating"),
            "score_100": review_factor_scores.get("ambience_rating", 0),
        },
        {
            "label": "Location",
            "average_rating": review_factor_averages.get("location_rating"),
            "score_100": review_factor_scores.get("location_rating", 0),
        },
        {
            "label": "Value",
            "average_rating": review_factor_averages.get("value_rating"),
            "score_100": review_factor_scores.get("value_rating", 0),
        },
        {
            "label": "Dietary Accommodation",
            "average_rating": review_factor_averages.get(
                "dietary_accommodation_rating"
            ),
            "score_100": review_factor_scores.get("dietary_accommodation_rating", 0),
        },
        {
            "label": "Cleanliness",
            "average_rating": review_factor_averages.get("cleanliness_rating"),
            "score_100": review_factor_scores.get("cleanliness_rating", 0),
        },
    ]

    score_breakdown = current_score_data.get("score_breakdown", [])

    trend_rows = list(restaurant.inspections.order_by("-inspection_date", "-id")[:8])
    trend_rows.reverse()
    trend_points = []
    for inspection in trend_rows:
        point_score = compute_restaurant_composite_score(
            restaurant,
            as_of_date=inspection.inspection_date,
        )
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
                "review_count": int(point_score.get("review_count") or 0),
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
        "review_factor_breakdown": review_factor_breakdown,
        "trend_points": trend_points,
        "trend_summary": trend_summary,
        "neighborhood_comparison": neighborhood_comparison,
    }


def signin_page(request):
    """
    Sign In page - displays login form
    """
    context = {
        "is_authenticated": request.user.is_authenticated,
        "title": "Sign In",
    }
    return render(request, "nomz/splash.html", context)


def home(request):
    """
    Home page view - displays different content based on authentication status.
    Restaurant users are redirected to their profile instead.
    """
    # If user is authenticated
    if request.user.is_authenticated:
        # Redirect staff/admins to dashboard
        if request.user.is_staff or request.user.is_superuser:
            return redirect("dashboard")

        # Redirect restaurants to profile
        if hasattr(request.user, "userprofile"):
            if request.user.userprofile.role == "restaurant":
                return redirect("profile")

    recommended_restaurants = []
    recommendation_message = ""

    if request.user.is_authenticated and not (
        request.user.is_staff or request.user.is_superuser
    ):
        try:
            preferences = request.user.preferences
        except UserPreference.DoesNotExist:
            preferences = None

        # Fetch restaurants shared by the user to exclude them from their own discovery section
        # This ensures we don't recommend back to the user what they've already suggested to others
        my_shared_ids = set(
            FriendMessage.objects.filter(
                sender=request.user, restaurant_recommendation__isnull=False
            ).values_list("restaurant_recommendation_id", flat=True)
        )

        my_shared_ids.update(
            FriendSharedRestaurant.objects.filter(added_by=request.user).values_list(
                "restaurant_id", flat=True
            )
        )

        # 1. System Recommendations (ONLY if preferences are set with actual criteria)
        has_set_preferences = preferences and (
            preferences.favorite_cuisines or preferences.neighborhood_preference
        )

        if has_set_preferences:
            system_recs = recommend_restaurants_for_user(
                request.user, limit=10
            )  # Fetch more to allow for filtering
            for r in system_recs:
                if r.id not in my_shared_ids:
                    recommended_restaurants.append(
                        {
                            "restaurant": r,
                            "source": "System",
                            "reason": "Based on your preferences",
                        }
                    )
                    if len(recommended_restaurants) >= 4:
                        break
        else:
            recommendation_message = (
                "Set your dining preferences so we can recommend restaurants for you."
            )

        # 2. Friend Recommendations (Received in chats)
        friend_messages = (
            FriendMessage.objects.filter(
                Q(conversation__participants=request.user)
                | Q(conversation__user1=request.user)
                | Q(conversation__user2=request.user)
            )
            .filter(restaurant_recommendation__isnull=False)
            .exclude(sender=request.user)
            .select_related("sender", "restaurant_recommendation")
            .order_by("-created_at")[:20]
        )

        # 3. Together List (Shared restaurants by others)
        shared_restaurants = (
            FriendSharedRestaurant.objects.filter(
                Q(conversation__participants=request.user)
                | Q(conversation__user1=request.user)
                | Q(conversation__user2=request.user)
            )
            .exclude(added_by=request.user)
            .select_related("added_by", "restaurant")
            .order_by("-created_at")[:20]
        )

        # Use a dict to avoid duplicate restaurants, prioritizing Friend recommendations
        seen_ids = set()
        final_list = []

        # Add friend recs
        for msg in friend_messages:
            if (
                msg.restaurant_recommendation.id not in seen_ids
                and msg.restaurant_recommendation.id not in my_shared_ids
            ):
                final_list.append(
                    {
                        "restaurant": msg.restaurant_recommendation,
                        "source": "Friend",
                        "sender": msg.sender.username,
                        "reason": f"Recommended by {msg.sender.username}",
                    }
                )
                seen_ids.add(msg.restaurant_recommendation.id)

        # Add shared list recs
        for shared in shared_restaurants:
            if (
                shared.restaurant.id not in seen_ids
                and shared.restaurant.id not in my_shared_ids
            ):
                final_list.append(
                    {
                        "restaurant": shared.restaurant,
                        "source": "Friend",
                        "sender": shared.added_by.username,
                        "reason": f"Added to Together List by {shared.added_by.username}",
                    }
                )
                seen_ids.add(shared.restaurant.id)

        # Add system recs
        for item in recommended_restaurants:
            if item["restaurant"].id not in seen_ids:
                final_list.append(item)
                seen_ids.add(item["restaurant"].id)

        recommended_restaurants = final_list[:8]  # Limit to 8 total

    context = {
        "title": "Home",
        "recommended_restaurants": recommended_restaurants,
        "recommendation_message": recommendation_message,
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
        Q(owner__userprofile__is_approved=True) | Q(owner__isnull=True),
        is_active=True,
        latitude__isnull=False,
        longitude__isnull=False,
        latitude__gte=NYC_MIN_LAT,
        latitude__lte=NYC_MAX_LAT,
        longitude__gte=NYC_MIN_LON,
        longitude__lte=NYC_MAX_LON,
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
    sort_by = normalize_sort_key(request.GET.get("sort_by", "composite_desc"))

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
    Legacy secure login for the built-in emergency admin account (AdminLoginForm + security code).

    Staff with normal Nomz accounts should use the React app Sign In (/api/auth/login/); that flow
    uses standard authentication and 2FA when enabled. This view is not duplicated in the SPA.
    """
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect("dashboard")
        else:
            logout(request)  # Logout if non-admin somehow got here

    if request.method == "POST":
        form = AdminLoginForm(request, data=request.POST)
        username = request.POST.get("username")

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Admin session established for {username}.")
            return redirect("dashboard")
        else:
            # Login failures are logged by signals
            pass
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

    # Identify users with suspicious login activity
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

    Renders nomz/restaurant_dashboard.html, nomz/admin_dashboard.html, or nomz/user_dashboard.html
    by role. templates/nomz/dashboard.html is legacy and is not referenced by this view.
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

    # 3. Recommendations - powered by saved preferences
    recommended_restaurants = []
    recommendation_message = ""
    if preferences:
        recommended_restaurants = recommend_restaurants_for_user(request.user, limit=8)
        if not recommended_restaurants:
            recommendation_message = (
                "No restaurants match your saved preferences yet. "
                "Try expanding cuisine options, price range, or neighborhood."
            )
    else:
        recommendation_message = (
            "Please save your dining preferences to show personalized recommendations."
        )

    context = {
        "title": "Dashboard",
        "user": request.user,
        "role": role,
        "preferences": preferences,  # Add this to context
        "recommended_restaurants": recommended_restaurants,
        "recommendation_message": recommendation_message,
        "is_approved": (
            getattr(request.user.userprofile, "is_approved", True)
            if hasattr(request.user, "userprofile")
            else True
        ),
        "is_rejected": (
            getattr(request.user.userprofile, "is_rejected", False)
            if hasattr(request.user, "userprofile")
            else False
        ),
        "reviews_written": Review.objects.filter(user=request.user).count(),
    }

    if role == "restaurant":
        # Get the restaurant profile for the restaurant owner
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        unread_notification_queryset = MessageNotification.objects.filter(
            recipient=request.user,
            is_read=False,
        )
        unread_message_notifications = unread_notification_queryset.select_related(
            "conversation",
            "conversation__restaurant",
            "conversation__diner",
            "triggered_by",
            "message",
        ).order_by("-created_at")[:8]
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
        context["unread_message_notifications"] = unread_message_notifications
        context["unread_message_notifications_count"] = (
            unread_notification_queryset.count()
        )
        context["active_claim"] = active_claim
        context["recent_claims"] = recent_claims
        if restaurant:
            context.update(_build_restaurant_score_insights(restaurant))
            # Fetch reviews
            reviews = (
                restaurant.reviews.select_related("user", "restaurant_response")
                .all()
                .order_by("-created_at")
            )
            context["reviews"] = reviews

            # Calculate average rating
            avg_rating = reviews.filter(is_deleted=False).aggregate(Avg("rating"))[
                "rating__avg"
            ]
            context["average_rating"] = round(avg_rating, 1) if avg_rating else None
        return render(request, "nomz/restaurant_dashboard.html", context)
    elif role == "admin":
        # Enhanced metrics for Issue #45 and #46
        # Fetch all user profiles for management
        all_users = (
            User.objects.all().select_related("userprofile").order_by("-date_joined")
        )
        diner_count = UserProfile.objects.filter(role="diner").count()
        restaurant_count = Restaurant.objects.count()

        # Recent activities (Logins)
        recent_logins = LoginLog.objects.all().order_by("-timestamp")[:10]

        # Security stats
        suspicious_count = LoginLog.objects.filter(is_suspicious=True).count()

        # Business account approvals metrics (Issue #53)
        pending_approval_count = UserProfile.objects.filter(
            role="restaurant", is_approved=False, is_rejected=False
        ).count()

        approved_business_count = UserProfile.objects.filter(
            role="restaurant", is_approved=True
        ).count()

        rejected_business_count = UserProfile.objects.filter(
            role="restaurant", is_rejected=True
        ).count()
        # Moderation metrics
        pending_report_count = ModerationReport.objects.filter(status="PENDING").count()

        recent_score_history = list(
            CompositeScoreHistory.objects.select_related(
                "restaurant",
                "triggered_by",
            ).order_by("-calculated_at")[:12]
        )
        open_score_anomalies = list(
            CompositeScoreAnomaly.objects.select_related(
                "restaurant",
                "score_history",
            )
            .filter(is_resolved=False)
            .order_by("-created_at")[:12]
        )
        open_score_anomaly_total = CompositeScoreAnomaly.objects.filter(
            is_resolved=False
        ).count()
        last_day = timezone.now() - timedelta(days=1)
        score_recalcs_last_day = CompositeScoreHistory.objects.filter(
            calculated_at__gte=last_day
        ).count()
        restaurants_recalculated_last_day = (
            CompositeScoreHistory.objects.filter(calculated_at__gte=last_day)
            .values("restaurant_id")
            .distinct()
            .count()
        )
        high_severity_anomalies = CompositeScoreAnomaly.objects.filter(
            is_resolved=False,
            severity__in=["HIGH", "CRITICAL"],
        ).count()
        score_recalc_restaurants = Restaurant.objects.order_by("name", "id").values(
            "id", "name"
        )

        context.update(
            {
                "all_users": all_users,
                "diner_count": diner_count,
                "restaurant_count": restaurant_count,
                "recent_logins": recent_logins,
                "suspicious_count": suspicious_count,
                "total_users": User.objects.count(),
                "approved_business_count": approved_business_count,
                "pending_approval_count": pending_approval_count,
                "rejected_business_count": rejected_business_count,
                "pending_report_count": pending_report_count,
                "recent_score_history": recent_score_history,
                "open_score_anomalies": open_score_anomalies,
                "open_score_anomaly_count": open_score_anomaly_total,
                "score_recalcs_last_day": score_recalcs_last_day,
                "restaurants_recalculated_last_day": restaurants_recalculated_last_day,
                "high_severity_anomalies": high_severity_anomalies,
                "score_algorithm_version": SCORE_ALGORITHM_VERSION,
                "score_recalc_restaurants": score_recalc_restaurants,
            }
        )
        return render(request, "nomz/admin_dashboard.html", context)
    else:
        # This matches the user_dashboard.html where your taste profile code is
        return render(request, "nomz/user_dashboard.html", context)


@staff_member_required
@require_POST
def admin_recalculate_scores(request):
    restaurant_id = (request.POST.get("restaurant_id") or "").strip()
    restaurant_name = (request.POST.get("restaurant_name") or "").strip()

    queryset = Restaurant.objects.all().order_by("id")
    if restaurant_id:
        try:
            queryset = queryset.filter(id=int(restaurant_id))
        except ValueError:
            messages.error(request, "Restaurant ID must be a number.")
            return redirect("dashboard")
    elif restaurant_name:
        exact_matches = queryset.filter(name__iexact=restaurant_name)
        exact_count = exact_matches.count()
        if exact_count == 1:
            queryset = exact_matches
        elif exact_count > 1:
            messages.error(
                request,
                "Multiple restaurants share that name. Please pick one from the dropdown.",
            )
            return redirect("dashboard")
        else:
            partial_matches = queryset.filter(name__icontains=restaurant_name)
            partial_count = partial_matches.count()
            if partial_count == 1:
                queryset = partial_matches
            elif partial_count > 1:
                messages.error(
                    request,
                    "Multiple restaurants match that name. Please pick one from the dropdown.",
                )
                return redirect("dashboard")
            else:
                messages.error(request, "No restaurant found with that name.")
                return redirect("dashboard")
    # If no id/name is provided, recompute for ALL restaurants by design.

    total = queryset.count()
    if total == 0:
        messages.info(request, "No restaurants matched the recalculation criteria.")
        return redirect("dashboard")

    updated = 0
    anomaly_count = 0
    for restaurant in queryset.iterator():
        score_data = refresh_restaurant_composite(
            restaurant,
            trigger_source="admin_dashboard",
            triggered_by=request.user,
            trigger_note="Admin dashboard trigger",
        )
        updated += 1
        anomaly_count += int(score_data.get("anomaly_count") or 0)

    SystemAuditLog.objects.create(
        actor_user=request.user,
        actor_username=request.user.username,
        level="INFO",
        action="admin_composite_score_recalculation",
        request_path=request.path,
        http_method=request.method,
        ip_address=request.META.get("REMOTE_ADDR"),
        metadata={
            "restaurant_id_filter": restaurant_id or None,
            "restaurant_name_filter": restaurant_name or None,
            "restaurants_updated": updated,
            "anomaly_flags_detected": anomaly_count,
        },
    )

    messages.success(
        request,
        (
            f"Recalculated scores for {updated}/{total} restaurant(s). "
            f"Detected {anomaly_count} anomaly flag(s)."
        ),
    )
    return redirect("dashboard")


@staff_member_required
@require_POST
def admin_resolve_score_anomaly(request, anomaly_id):
    anomaly = get_object_or_404(CompositeScoreAnomaly, id=anomaly_id)
    if not anomaly.is_resolved:
        anomaly.is_resolved = True
        anomaly.resolved_at = timezone.now()
        anomaly.resolved_by = request.user
        anomaly.save(update_fields=["is_resolved", "resolved_at", "resolved_by"])

        SystemAuditLog.objects.create(
            actor_user=request.user,
            actor_username=request.user.username,
            level="INFO",
            action="admin_score_anomaly_resolved",
            request_path=request.path,
            http_method=request.method,
            ip_address=request.META.get("REMOTE_ADDR"),
            metadata={
                "anomaly_id": anomaly.id,
                "restaurant_id": anomaly.restaurant_id,
                "anomaly_type": anomaly.anomaly_type,
            },
        )
        messages.success(request, f"Anomaly #{anomaly.id} marked as resolved.")
    else:
        messages.info(request, f"Anomaly #{anomaly.id} is already resolved.")
    return redirect("dashboard")


def is_restaurant_owner(user):
    """Helper function to check if user is a restaurant owner"""
    return hasattr(user, "userprofile") and user.userprofile.role == "restaurant"


@login_required(login_url="landing")
def restaurant_profile(request):
    """
    View restaurant owner's profile page
    Shows restaurant details, photos, and status
    """
    if not is_restaurant_owner(request.user):
        messages.error(request, "You do not have permission to access this page.")
        return redirect("dashboard")

    restaurant = Restaurant.objects.filter(owner=request.user).first()
    context = {
        "title": "Restaurant Profile",
        "restaurant": restaurant,
        "user": request.user,
        "is_approved": request.user.userprofile.is_approved,
        "is_rejected": request.user.userprofile.is_rejected,
    }
    if restaurant:
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
            profile = request.user.userprofile

            major_fields = {"name", "address", "phone", "website", "email"}
            requires_approval = any(
                field in major_fields for field in form.changed_data
            )

            if requires_approval:
                profile.is_approved = False
                profile.is_rejected = False
                profile.save()
                messages.success(
                    request, "Restaurant profile updated and re-submitted for approval!"
                )
            else:
                messages.success(request, "Restaurant profile updated successfully!")

            form.save()
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


@login_required(login_url="login")
def restaurant_search(request):
    query = request.GET.get("q", "").strip()
    neighborhood = request.GET.get("neighborhood", "").strip()
    sort_by = normalize_sort_key(request.GET.get("sort_by", "composite_desc"))

    base_restaurants = Restaurant.objects.filter(
        Q(owner__userprofile__is_approved=True) | Q(owner__isnull=True), is_active=True
    )
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

    base_restaurants = sort_restaurant_queryset(base_restaurants, sort_by)

    results = []
    for restaurant in base_restaurants:
        fallback_cuisine = restaurant.cuisine or restaurant.cuisine_type or ""
        if not fallback_cuisine and restaurant.cuisine_tags:
            fallback_cuisine = ", ".join(
                str(tag) for tag in restaurant.cuisine_tags[:3]
            )
        results.append(
            {
                "id": restaurant.id,
                "name": restaurant.name,
                "description": restaurant.description or "",
                "cuisine": fallback_cuisine,
                "neighborhood": restaurant.neighborhood or restaurant.borough or "",
                "composite_score": restaurant.composite_score,
                "price_label": restaurant.get_price_range_display(),
                "rating_score": restaurant.grade_score_latest,
                "is_flagged": restaurant.is_flagged,
            }
        )

    all_neighborhoods = sorted(
        {
            r.neighborhood or r.borough
            for r in Restaurant.objects.filter(
                Q(owner__userprofile__is_approved=True) | Q(owner__isnull=True),
                is_active=True,
            )
            if (r.neighborhood or r.borough)
        }
    )

    return render(
        request,
        "nomz/search_results.html",
        {
            "results": results,
            "query": query,
            "neighborhood": neighborhood,
            "sort_by": sort_by,
            "all_neighborhoods": all_neighborhoods,
        },
    )


# Add this to views.py


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


@login_required(login_url="landing")
@login_required
def recommendations(request):
    """Show personalized restaurant recommendations combined with friend insights."""
    from django.db.models import Q
    from .models import FriendConversation, FriendMessage, UserPreference
    from .restaurant_sorting import recommend_restaurants_for_user

    # 1. Fetch Social Recommendations (Robust Query)
    conv_ids = FriendConversation.objects.filter(
        Q(participants=request.user) | Q(user1=request.user) | Q(user2=request.user)
    ).values_list('id', flat=True)

    messages = FriendMessage.objects.filter(
        conversation_id__in=conv_ids,
        restaurant_recommendation__isnull=False,
        restaurant_recommendation__is_active=True
    ).exclude(sender=request.user).select_related('restaurant_recommendation', 'sender').order_by('-created_at')

    social_data = [] # List of (restaurant, sender_name)
    seen_ids = set()
    for m in messages:
        rid = m.restaurant_recommendation.id
        if rid not in seen_ids:
            social_data.append((m.restaurant_recommendation, m.sender.username))
            seen_ids.add(rid)
        if len(social_data) >= 5:
            break

    # 2. Fetch System Recommendations
    system_data = []
    try:
        # Check if user has meaningful preferences set up (Price alone doesn't count as setup)
        prefs = getattr(request.user, "preferences", None)
        nh = (prefs.neighborhood_preference or "").strip() if prefs else ""
        has_prefs = prefs and (
            (prefs.favorite_cuisines and len(prefs.favorite_cuisines) > 0) or 
            (prefs.dietary_restrictions and len(prefs.dietary_restrictions) > 0) or 
            nh
        )
        
        if has_prefs:
            recommended = recommend_restaurants_for_user(request.user, limit=20)
            for r in recommended:
                if r.id not in seen_ids:
                    system_data.append((r, None)) # None means system recommended
                    seen_ids.add(r.id)
    except Exception:
        pass

    final_recommendations = social_data + system_data
    recommendation_message = ""
    if not final_recommendations:
        recommendation_message = "Set your preferences in your profile or chat with friends to see recommendations here!"

    return render(
        request,
        "nomz/recommendations.html",
        {
            "title": "Recommendations",
            "final_recommendations": final_recommendations[:15],
            "recommendation_message": recommendation_message,
        },
    )


@login_required(login_url="landing")
@require_POST
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


@staff_member_required
def admin_pending_approvals(request):
    """
    Dedicated view to manage pending restaurant registrations and ownership claims.
    """
    pending_approvals = (
        User.objects.filter(userprofile__role="restaurant")
        .filter(
            Q(userprofile__is_approved=False, userprofile__is_rejected=False)
            | Q(restaurant_claims__status=RestaurantOwnershipClaim.STATUS_PENDING)
        )
        .distinct()
        .select_related("userprofile")
        .order_by("-date_joined")
    )
    pending_claims = (
        RestaurantOwnershipClaim.objects.filter(
            status=RestaurantOwnershipClaim.STATUS_PENDING
        )
        .select_related("restaurant", "claimant")
        .order_by("-created_at")
    )
    claims_by_user_id = {claim.claimant_id: claim for claim in pending_claims}
    for pending_user in pending_approvals:
        pending_user.pending_claim = claims_by_user_id.get(pending_user.id)

    context = {
        "title": "Pending Approvals",
        "pending_approvals": pending_approvals,
        "pending_claim_count": pending_claims.count(),
    }
    return render(request, "nomz/admin_pending_approvals.html", context)


@staff_member_required
@require_POST
def admin_approve_restaurant(request, user_id):
    """
    Approve a pending restaurant owner account and, when present, approve
    the user's pending ownership claim.
    """
    user_to_approve = get_object_or_404(User, id=user_id)
    pending_claim = (
        RestaurantOwnershipClaim.objects.filter(
            claimant=user_to_approve,
            status=RestaurantOwnershipClaim.STATUS_PENDING,
        )
        .select_related("restaurant")
        .first()
    )

    if pending_claim:
        try:
            pending_claim.approve(
                reviewer=request.user,
                notes="Approved via admin pending approvals dashboard.",
            )
        except ValidationError as exc:
            messages.error(
                request,
                f"Could not approve ownership claim for {user_to_approve.username}: {exc}",
            )
            return redirect("admin_pending_approvals")

    if hasattr(user_to_approve, "userprofile"):
        profile = user_to_approve.userprofile
        profile.is_approved = True
        profile.is_rejected = False
        profile.save()

    if pending_claim:
        messages.success(
            request,
            f"Approved {user_to_approve.username} and assigned ownership of "
            f'"{pending_claim.restaurant.name}".',
        )
    else:
        messages.success(
            request, f"Restaurant account for {user_to_approve.username} approved!"
        )
    return redirect("admin_pending_approvals")


@staff_member_required
def admin_approved_accounts(request):
    """
    Dedicated view to manage already approved restaurant accounts.
    """
    approved_accounts = (
        User.objects.filter(
            userprofile__role="restaurant", userprofile__is_approved=True
        )
        .select_related("userprofile")
        .order_by("-date_joined")
    )

    context = {
        "title": "Approved Accounts",
        "approved_accounts": approved_accounts,
    }
    return render(request, "nomz/admin_approved_list.html", context)


@staff_member_required
def admin_rejected_accounts(request):
    """
    Dedicated view to manage rejected restaurant accounts.
    """
    rejected_accounts = (
        User.objects.filter(
            userprofile__role="restaurant", userprofile__is_rejected=True
        )
        .select_related("userprofile")
        .order_by("-date_joined")
    )

    context = {
        "title": "Rejected Accounts",
        "rejected_accounts": rejected_accounts,
    }
    return render(request, "nomz/admin_rejected_list.html", context)


@staff_member_required
@require_POST
def admin_reject_restaurant(request, user_id):
    """
    Reject a restaurant owner account and reject pending ownership claim(s) if any.
    """
    user_to_reject = get_object_or_404(User, id=user_id)
    # We NO LONGER set is_active=False to allow login as requested.

    pending_claims = RestaurantOwnershipClaim.objects.filter(
        claimant=user_to_reject,
        status=RestaurantOwnershipClaim.STATUS_PENDING,
    )
    rejected_claim_count = 0
    for claim in pending_claims:
        claim.reject(
            reviewer=request.user,
            notes="Rejected via admin pending approvals dashboard.",
        )
        rejected_claim_count += 1

    if hasattr(user_to_reject, "userprofile"):
        profile = user_to_reject.userprofile
        profile.is_approved = False
        profile.is_rejected = True
        profile.save()

    if rejected_claim_count:
        messages.warning(
            request,
            f"Restaurant account for {user_to_reject.username} rejected. "
            f"{rejected_claim_count} pending ownership claim(s) were also rejected.",
        )
    else:
        messages.warning(
            request,
            f"Restaurant account for {user_to_reject.username} has been REJECTED.",
        )
    return redirect("admin_pending_approvals")


# ============================================================================
# MODERATION & REVIEW VIEWS
# ============================================================================


@login_required(login_url="landing")
def add_review(request, restaurant_id):
    """
    Allow users to submit a review for a restaurant.
    """
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.restaurant = restaurant
            review.user = request.user
            review.save()
            messages.success(request, "Your review has been posted!")
            return redirect("restaurant_search")
    else:
        form = ReviewForm()

    context = {
        "title": f"Review {restaurant.name}",
        "form": form,
        "restaurant": restaurant,
    }
    return render(request, "nomz/add_review.html", context)


@login_required(login_url="landing")
@require_POST
def respond_to_review(request, review_id):
    """
    Allow a restaurant owner to create or edit one public response per review.
    """
    review = get_object_or_404(
        Review.objects.select_related("restaurant", "restaurant__owner"),
        id=review_id,
    )
    restaurant = review.restaurant

    if restaurant.owner_id != request.user.id:
        return HttpResponseForbidden(
            "Only the owner of this restaurant can respond to this review."
        )

    if review.is_deleted:
        messages.error(
            request,
            "You cannot respond to a review that was removed by moderation.",
        )
        return redirect("profile")

    form = ReviewResponseForm(request.POST)
    if form.is_valid():
        response_text = form.cleaned_data["response_text"]
        review_response, created = ReviewResponse.objects.get_or_create(
            review=review,
            defaults={
                "restaurant": restaurant,
                "responder": request.user,
                "response_text": response_text,
            },
        )
        if not created:
            review_response.response_text = response_text
            review_response.restaurant = restaurant
            review_response.responder = request.user
            review_response.save(
                update_fields=[
                    "response_text",
                    "restaurant",
                    "responder",
                    "updated_at",
                ]
            )
            messages.success(request, "Your public response has been updated.")
        else:
            messages.success(request, "Your public response has been posted.")
    else:
        messages.error(
            request,
            "Could not save response. Please make sure the response text is valid.",
        )

    next_url = (request.POST.get("next") or "").strip()
    if next_url.startswith("/"):
        return redirect(next_url)
    return redirect("profile")


@login_required(login_url="landing")
def report_content(request, content_type, content_id):
    """
    Allow users to report a review or another user.
    """
    review = None
    reported_user = None

    if content_type == "review":
        review = get_object_or_404(Review, id=content_id)
    elif content_type == "user":
        reported_user = get_object_or_404(User, id=content_id)
    else:
        messages.error(request, "Invalid report target.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ModerationReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.review = review
            report.reported_user = reported_user
            report.save()
            messages.success(
                request, "Thank you. Your report has been submitted for review."
            )
            return redirect("dashboard")
    else:
        form = ModerationReportForm()

    context = {
        "title": "Report Content",
        "form": form,
        "content_type": content_type,
        "target": review or reported_user,
    }
    return render(request, "nomz/report_content.html", context)


@staff_member_required
def admin_moderation_dashboard(request):
    """
    Dashboard for admins to manage pending reports.
    """
    pending_reports = ModerationReport.objects.filter(status="PENDING").order_by(
        "-created_at"
    )
    resolved_reports = ModerationReport.objects.exclude(status="PENDING").order_by(
        "-created_at"
    )[:20]

    context = {
        "title": "Moderation Dashboard",
        "pending_reports": pending_reports,
        "resolved_reports": resolved_reports,
    }
    return render(request, "nomz/admin_moderation.html", context)


@staff_member_required
@require_POST
def admin_resolve_report(request, report_id):
    """
    Admins can take action on a report.
    """
    report = get_object_or_404(ModerationReport, id=report_id)
    action = request.POST.get("action")
    moderator_note = request.POST.get("moderator_note", "")

    if action == "dismiss":
        report.status = "DISMISSED"
        report.action_taken = "No action taken"
    elif action == "flag_fraud":
        if report.review:
            report.review.is_flagged = True
            report.review.save()
            report.action_taken = "Review flagged as fraudulent"
        elif report.reported_user:
            # Set flag on UserProfile
            if hasattr(report.reported_user, "userprofile"):
                report.reported_user.userprofile.is_flagged = True
                report.reported_user.userprofile.save()

            # Set flag on all Restaurants owned by this user
            Restaurant.objects.filter(owner=report.reported_user).update(
                is_flagged=True
            )

            report.action_taken = "User and associated restaurant(s) flagged for fraud"
        report.status = "RESOLVED"
    elif action == "unflag":
        if report.review:
            report.review.is_flagged = False
            report.review.save()
            report.action_taken = "Review un-flagged"
        elif report.reported_user:
            # Remove flag on UserProfile
            if hasattr(report.reported_user, "userprofile"):
                report.reported_user.userprofile.is_flagged = False
                report.reported_user.userprofile.save()

            # Remove flag on all Restaurants owned by this user
            Restaurant.objects.filter(owner=report.reported_user).update(
                is_flagged=False
            )

            report.action_taken = "User and associated restaurant(s) un-flagged"
        report.status = "PENDING"
    elif action == "delete":
        if report.review:
            report.review.is_deleted = True
            report.review.save()
            report.action_taken = "Review soft-deleted"
        report.status = "RESOLVED"
    elif action == "reevaluate":
        report.status = "PENDING"
        report.action_taken = "Moved back to pending for re-evaluation"

    report.moderator_note = moderator_note
    report.resolved_at = timezone.now()
    report.save()

    # Audit logging
    SystemAuditLog.objects.create(
        actor_user=request.user,
        actor_username=request.user.username,
        level="WARNING" if action != "dismiss" else "INFO",
        action=f"moderation_{action}",
        request_path=request.path,
        http_method=request.method,
        ip_address=request.META.get("REMOTE_ADDR"),
        metadata={
            "report_id": report.id,
            "action": action,
            "target": str(report),
        },
    )

    messages.success(request, f"Report {report_id} has been {report.status.lower()}.")
    return redirect("admin_moderation_dashboard")


@login_required(login_url="landing")
def restaurant_detail(request, restaurant_id):
    """
    Public detail page for a restaurant to view info and reviews.
    """
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    reviews = (
        restaurant.reviews.select_related("user", "restaurant_response")
        .filter(is_deleted=False)
        .order_by("-created_at")
    )
    return render(
        request,
        "nomz/restaurant_detail.html",
        {"restaurant": restaurant, "reviews": reviews},
    )


@login_required(login_url="landing")
def message_inbox(request):
    from django.db.models import Count, Q

    if is_restaurant_owner(request.user):
        conversations = (
            Conversation.objects.filter(restaurant__owner=request.user)
            .select_related("restaurant", "diner")
            .annotate(
                unread_count=Count(
                    "messages",
                    filter=Q(messages__is_read=False)
                    & ~Q(messages__sender=request.user),
                )
            )
            .order_by("-updated_at")
        )
    else:
        conversations = (
            Conversation.objects.filter(diner=request.user)
            .select_related("restaurant", "diner")
            .annotate(
                unread_count=Count(
                    "messages",
                    filter=Q(messages__is_read=False)
                    & ~Q(messages__sender=request.user),
                )
            )
            .order_by("-updated_at")
        )

    return render(
        request,
        "nomz/message_inbox.html",
        {
            "title": "Messages",
            "conversations": conversations,
        },
    )


@login_required(login_url="landing")
def message_restaurant(request, restaurant_id):
    if is_restaurant_owner(request.user):
        messages.error(
            request,
            "Restaurant owner accounts cannot start a diner-to-restaurant conversation.",
        )
        return redirect("restaurant_detail", restaurant_id=restaurant_id)

    restaurant = get_object_or_404(
        Restaurant.objects.select_related("owner"), id=restaurant_id
    )
    if not restaurant.owner_id:
        messages.error(
            request,
            "This restaurant does not yet have an owner account for messaging.",
        )
        return redirect("restaurant_detail", restaurant_id=restaurant_id)

    # Issue #62: respect the restaurant's messaging toggle
    if not restaurant.messaging_enabled:
        messages.error(
            request,
            f"{restaurant.name} has messaging disabled and is not accepting new messages at this time.",
        )
        return redirect("restaurant_detail", restaurant_id=restaurant_id)

    conversation, _ = Conversation.objects.get_or_create(
        restaurant=restaurant,
        diner=request.user,
    )
    return redirect("conversation_detail", conversation_id=conversation.id)


@login_required(login_url="landing")
@require_http_methods(["GET", "POST"])
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.select_related("restaurant", "restaurant__owner", "diner"),
        id=conversation_id,
    )
    if not conversation.can_access(request.user):
        return HttpResponseForbidden("Permission denied")

    messaging_disabled = not conversation.restaurant.messaging_enabled
    unread_message_ids = list(
        Message.objects.filter(conversation=conversation, is_read=False)
        .exclude(sender=request.user)
        .values_list("id", flat=True)
    )
    if unread_message_ids:
        Message.objects.filter(id__in=unread_message_ids).update(is_read=True)
        MessageNotification.objects.filter(
            recipient=request.user,
            message_id__in=unread_message_ids,
            is_read=False,
        ).update(is_read=True, read_at=timezone.now())

    if request.method == "POST":
        # Issue #62: block sending when messaging is disabled (only for diners)
        if messaging_disabled and not is_restaurant_owner(request.user):
            messages.error(
                request,
                "This restaurant has messaging disabled and is not accepting messages.",
            )
            return redirect("conversation_detail", conversation_id=conversation.id)
        text = (request.POST.get("message") or "").strip()
        if not text:
            messages.error(request, "Message cannot be empty.")
            return redirect("conversation_detail", conversation_id=conversation.id)

        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            body=text,
        )
        conversation.save(update_fields=["updated_at"])
        return redirect("conversation_detail", conversation_id=conversation.id)

    thread_messages = conversation.messages.select_related("sender").order_by(
        "created_at"
    )
    return render(
        request,
        "nomz/conversation_detail.html",
        {
            "title": "Conversation",
            "conversation": conversation,
            "thread_messages": thread_messages,
            "messaging_disabled": messaging_disabled,
        },
    )


@login_required(login_url="landing")
@require_http_methods(["GET", "POST"])
def manage_communication_settings(request):
    """
    Allow restaurant owners to manage their communication settings:
    toggle messaging on/off and set available response hours. (Issue #62)
    """
    if not is_restaurant_owner(request.user):
        messages.error(
            request, "You do not have permission to manage communication settings."
        )
        return redirect("profile")

    restaurant = get_object_or_404(Restaurant, owner=request.user)

    if request.method == "POST":
        form = RestaurantCommunicationSettingsForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            if restaurant.messaging_enabled:
                messages.success(
                    request, "Messaging is now enabled for your restaurant."
                )
            else:
                messages.warning(
                    request,
                    "Messaging has been disabled. Diners will not be able to send you new messages.",
                )
            return redirect("profile")
    else:
        form = RestaurantCommunicationSettingsForm(instance=restaurant)

    context = {
        "title": "Communication Settings",
        "form": form,
        "restaurant": restaurant,
    }
    return render(request, "nomz/manage_communication_settings.html", context)


@login_required(login_url="landing")
def friends_chat_index(request):
    """Force redirect to modernized v2 interface."""
    return redirect("friends_chat_index_v2")


@login_required(login_url="landing")
def friends_chat_detail(request, username=None, conversation_id=None):
    """Force redirect to modernized v2 interface."""
    if conversation_id:
        return redirect("friends_chat_detail_v2_by_id", conversation_id=conversation_id)
    return redirect("friends_chat_detail_v2", username=username)


@login_required
def create_group_chat(request):
    """
    Creates a new group conversation.
    """
    if request.method == "POST":
        group_name = request.POST.get("group_name", "").strip()
        participant_ids = request.POST.getlist("participants")  # Multiple IDs

        if not group_name:
            messages.error(request, "Group name is required.")
            return redirect("friends_chat_index")

        conv = FriendConversation.objects.create(
            name=group_name, is_group=True, creator=request.user  # Set creator
        )
        conv.participants.add(request.user)  # Add self
        for p_id in participant_ids:
            try:
                user = User.objects.get(id=p_id)
                # Ensure only diners are added
                if hasattr(user, "userprofile") and user.userprofile.role == "diner":
                    conv.participants.add(user)
            except User.DoesNotExist:
                continue

        return redirect("friends_chat_detail_by_id", conversation_id=conv.id)

    return redirect("friends_chat_index")


@login_required
def manage_group_member(request, conversation_id):
    """
    Allows the group admin (creator) to add or remove members.
    """
    conv = get_object_or_404(FriendConversation, id=conversation_id, is_group=True)
    if conv.creator != request.user:
        messages.error(request, "Only the group creator can manage members.")
        return redirect("friends_chat_detail_by_id", conversation_id=conversation_id)

    if request.method == "POST":
        action = request.POST.get("action")
        username = request.POST.get("username", "").strip()
        user_id = request.POST.get("user_id")

        user = None
        if user_id:
            user = User.objects.filter(id=user_id).first()
        elif username:
            user = User.objects.filter(username=username).first()

        if user:
            if action == "add":
                # Ensure only diners are added
                if hasattr(user, "userprofile") and user.userprofile.role == "diner":
                    conv.participants.add(user)
                    messages.success(request, f"Added {user.username} to the group.")
                else:
                    messages.error(request, "Only diners can be added to chat groups.")
            elif action == "remove":
                if user == conv.creator:
                    messages.error(
                        request, "You cannot remove yourself from a group you created."
                    )
                else:
                    conv.participants.remove(user)
                    messages.success(
                        request, f"Removed {user.username} from the group."
                    )

    return redirect("friends_chat_detail_by_id", conversation_id=conversation_id)


@login_required
def leave_group(request, conversation_id):
    """
    Allows a member to leave a group.
    """
    conv = get_object_or_404(FriendConversation, id=conversation_id, is_group=True)
    if not conv.can_access(request.user):
        return redirect("friends_chat_index")

    if conv.creator == request.user:
        messages.error(
            request,
            "Creators cannot leave their own groups. Use 'Delete Group' (if available) or assign a new admin.",
        )
        return redirect("friends_chat_detail_by_id", conversation_id=conversation_id)

    conv.participants.remove(request.user)
    messages.success(request, f"You have left the group '{conv.name}'.")
    return redirect("friends_chat_index")


@login_required
def recommend_friend_restaurant(request, username=None, conversation_id=None):
    """
    Sends a restaurant recommendation to a chat or group.
    """
    if conversation_id:
        conversation = get_object_or_404(FriendConversation, id=conversation_id)
    else:
        target_user = get_object_or_404(User, username=username)
        user1, user2 = (
            (request.user, target_user)
            if request.user.id < target_user.id
            else (target_user, request.user)
        )
        conversation = get_object_or_404(
            FriendConversation, user1=user1, user2=user2, is_group=False
        )

    if request.method == "POST":
        restaurant_id = request.POST.get("restaurant_id")
        restaurant_name = request.POST.get("restaurant_name")
        body = request.POST.get("body", "")

        restaurant = None
        if restaurant_id:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        elif restaurant_name:
            restaurant = Restaurant.objects.filter(name=restaurant_name).first()

        if restaurant:
            FriendMessage.objects.create(
                conversation=conversation,
                sender=request.user,
                body=body,
                restaurant_recommendation=restaurant,
            )
            conversation.save()  # Update updated_at

    if conversation_id:
        return redirect("friends_chat_detail_by_id", conversation_id=conversation_id)
    return redirect("friends_chat_detail", username=username)


@login_required
def toggle_shared_restaurant(request, username=None, conversation_id=None):
    """
    Adds or removes a restaurant from the shared 'Together List' in a chat or group.
    """
    if conversation_id:
        conversation = get_object_or_404(FriendConversation, id=conversation_id)
    else:
        target_user = get_object_or_404(User, username=username)
        user1, user2 = (
            (request.user, target_user)
            if request.user.id < target_user.id
            else (target_user, request.user)
        )
        conversation = get_object_or_404(
            FriendConversation, user1=user1, user2=user2, is_group=False
        )

    if request.method == "POST":
        restaurant_id = request.POST.get("restaurant_id")
        restaurant_name = request.POST.get("restaurant_name")
        action = request.POST.get("action", "add")

        restaurant = None
        if restaurant_id:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        elif restaurant_name:
            restaurant = Restaurant.objects.filter(name=restaurant_name).first()

        if restaurant:
            if action == "add":
                FriendSharedRestaurant.objects.get_or_create(
                    conversation=conversation,
                    restaurant=restaurant,
                    defaults={"added_by": request.user},
                )
            elif action == "remove":
                FriendSharedRestaurant.objects.filter(
                    conversation=conversation, restaurant=restaurant
                ).delete()

    if conversation_id:
        return redirect("friends_chat_detail_by_id", conversation_id=conversation_id)
    return redirect("friends_chat_detail", username=username)


# --- Modernized Friend Chat Views (v2) ---
# These views render the updated UI templates while preserving existing logic.
# They are added to maintain the "non-destructive" constraint.

@login_required(login_url="landing")
def friends_chat_index_v2(request):
    """Modernized index page for friend conversations."""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        if username:
            target_user = User.objects.filter(username__iexact=username, userprofile__role="diner").exclude(id=request.user.id).first()
            if target_user:
                return redirect("friends_chat_detail_v2", username=target_user.username)
            else:
                messages.error(request, f"Diner with username '{username}' not found.")
                return redirect("friends_chat_index_v2")

    conversations = FriendConversation.objects.filter(participants=request.user).distinct().order_by("-updated_at")
    other_users = User.objects.filter(userprofile__role="diner").exclude(id=request.user.id)

    context = {
        "title": "Chat with Friends",
        "conversations": conversations,
        "other_users": other_users,
        "all_restaurants": [],
    }
    return render(request, "nomz/friends_chat_v2.html", context)


@login_required(login_url="landing")
def friends_chat_detail_v2(request, username=None, conversation_id=None):
    """Modernized chat detail page for both 1-on-1 and group chats."""
    if conversation_id:
        conv = get_object_or_404(FriendConversation, id=conversation_id)
        if not conv.can_access(request.user):
            return redirect("friends_chat_index_v2")
        target_user = None
    else:
        target_user = get_object_or_404(User, username=username)
        if target_user == request.user:
            return redirect("friends_chat_index_v2")

        user1, user2 = (request.user, target_user) if request.user.id < target_user.id else (target_user, request.user)
        conv, created = FriendConversation.objects.get_or_create(user1=user1, user2=user2, is_group=False)
        if created:
            conv.participants.add(user1, user2)

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        if body:
            FriendMessage.objects.create(conversation=conv, sender=request.user, body=body)
            conv.updated_at = timezone.now()
            conv.save(update_fields=["updated_at"])

        if conversation_id:
            return redirect("friends_chat_detail_v2_by_id", conversation_id=conversation_id)
        return redirect("friends_chat_detail_v2", username=username)

    conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    chat_messages = conv.messages.all().select_related("sender", "restaurant_recommendation")
    shared_restaurants = conv.shared_restaurants.all().select_related("restaurant")
    all_restaurants = Restaurant.objects.all().order_by("name")
    all_users = User.objects.filter(userprofile__role="diner").exclude(id=request.user.id)
    participants = conv.get_participants()

    conversations = FriendConversation.objects.filter(participants=request.user).distinct()
    shared_restaurants_list = [sr.restaurant for sr in shared_restaurants]

    all_restaurants_list = [] # Switched to AJAX search for performance
    context = {
        "title": conv.name if conv.is_group else f"Chat with {target_user.username}",
        "target_user": target_user,
        "other_user": target_user,
        "conversation": conv,
        "chat_messages": chat_messages,
        "shared_restaurants": shared_restaurants,
        "shared_restaurants_list": shared_restaurants_list,
        "conversations": conversations,
        "all_restaurants": all_restaurants_list,
        "all_users": all_users,
        "participants": participants,
    }
    return render(request, "nomz/friends_chat_conversation_v2.html", context)


@login_required
def create_group_chat_v2(request):
    """Modernized group chat creation."""
    if request.method == "POST":
        group_name = request.POST.get("group_name", "").strip()
        participant_ids = request.POST.getlist("participants")
        if not group_name:
            messages.error(request, "Group name is required.")
            return redirect("friends_chat_index_v2")
        conv = FriendConversation.objects.create(name=group_name, is_group=True, creator=request.user)
        conv.participants.add(request.user)
        for p_id in participant_ids:
            try:
                user = User.objects.get(id=p_id)
                if hasattr(user, "userprofile") and user.userprofile.role == "diner":
                    conv.participants.add(user)
            except User.DoesNotExist:
                continue
        return redirect("friends_chat_detail_v2_by_id", conversation_id=conv.id)
    return redirect("friends_chat_index_v2")


@login_required
def manage_group_member_v2(request, conversation_id):
    """Modernized group member management."""
    conv = get_object_or_404(FriendConversation, id=conversation_id, is_group=True)
    if conv.creator != request.user:
        messages.error(request, "Only the group creator can manage members.")
        return redirect("friends_chat_detail_v2_by_id", conversation_id=conversation_id)
    if request.method == "POST":
        action = request.POST.get("action", "add")  # Default to add if not specified
        username = request.POST.get("username", "").strip()
        user_id = request.POST.get("user_id")
        user = None
        if user_id:
            user = User.objects.filter(id=user_id).first()
        elif username:
            user = User.objects.filter(username=username).first()
        if user:
            if action == "add":
                if hasattr(user, "userprofile") and user.userprofile.role == "diner":
                    conv.participants.add(user)
                    messages.success(request, f"Added {user.username} to the group.")
                else:
                    messages.error(request, "Only diners can be added to chat groups.")
            elif action == "remove":
                if user != conv.creator:
                    conv.participants.remove(user)
                    messages.success(request, f"Removed {user.username} from the group.")
                else:
                    messages.error(request, "You cannot remove yourself from a group you created.")
    return redirect("friends_chat_detail_v2_by_id", conversation_id=conversation_id)


@login_required
def leave_group_v2(request, conversation_id):
    """Modernized leave group functionality."""
    conv = get_object_or_404(FriendConversation, id=conversation_id, is_group=True)
    if not conv.can_access(request.user):
        return redirect("friends_chat_index_v2")
    if conv.creator == request.user:
        messages.error(request, "Creators cannot leave their own groups.")
        return redirect("friends_chat_detail_v2_by_id", conversation_id=conversation_id)
    conv.participants.remove(request.user)
    messages.success(request, f"You have left the group '{conv.name}'.")
    return redirect("friends_chat_index_v2")


@login_required
def recommend_friend_restaurant_v2(request, username=None, conversation_id=None):
    """Modernized restaurant recommendation."""
    if conversation_id:
        conversation = get_object_or_404(FriendConversation, id=conversation_id)
    else:
        target_user = get_object_or_404(User, username=username)
        user1, user2 = (request.user, target_user) if request.user.id < target_user.id else (target_user, request.user)
        conversation = get_object_or_404(FriendConversation, user1=user1, user2=user2, is_group=False)

    if request.method == "POST":
        restaurant_id = request.POST.get("restaurant_id")
        restaurant_name = request.POST.get("restaurant_name")
        body = request.POST.get("body", "")
        restaurant = None
        if restaurant_id:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        elif restaurant_name:
            restaurant = Restaurant.objects.filter(name=restaurant_name).first()
        if restaurant:
            FriendMessage.objects.create(conversation=conversation, sender=request.user, body=body, restaurant_recommendation=restaurant)
            conversation.save()

    if conversation_id:
        return redirect("friends_chat_detail_v2_by_id", conversation_id=conversation_id)
    return redirect("friends_chat_detail_v2", username=username)


@login_required
def toggle_shared_restaurant_v2(request, username=None, conversation_id=None):
    """Modernized Together List toggle."""
    if conversation_id:
        conversation = get_object_or_404(FriendConversation, id=conversation_id)
    else:
        target_user = get_object_or_404(User, username=username)
        user1, user2 = (request.user, target_user) if request.user.id < target_user.id else (target_user, request.user)
        conversation = get_object_or_404(FriendConversation, user1=user1, user2=user2, is_group=False)

    if request.method == "POST":
        restaurant_id = request.POST.get("restaurant_id")
        restaurant_name = request.POST.get("restaurant_name")
        action = request.POST.get("action", "add")
        restaurant = None
        if restaurant_id:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        elif restaurant_name:
            restaurant = Restaurant.objects.filter(name=restaurant_name).first()
        if restaurant:
            # Toggle logic: if exists, remove; else add.
            shared_qs = FriendSharedRestaurant.objects.filter(conversation=conversation, restaurant=restaurant)
            if shared_qs.exists():
                shared_qs.delete()
            else:
                FriendSharedRestaurant.objects.create(conversation=conversation, restaurant=restaurant, added_by=request.user)

    if conversation_id:
        return redirect("friends_chat_detail_v2_by_id", conversation_id=conversation_id)
    return redirect("friends_chat_detail_v2", username=username)


@login_required
@require_GET
def restaurant_search_api_v2(request):
    """
    Truly exhaustive search for chat.
    Searches Restaurants by all fields AND auto-creates profiles for Owners.
    Returns Top 10 recently updated if query is empty.
    """
    query = request.GET.get("search", "").strip()
    
    # 1. Handle Empty Query (Show Recent/Top)
    if not query:
        recent = Restaurant.objects.all().order_by("-updated_at")[:10]
        results = [{"id": r.id, "name": r.display_name or r.name} for r in recent]
        return JsonResponse({"results": results})
    
    # 2. Match Owners (Auto-Create Stub if missing)
    matching_owners = User.objects.filter(
        userprofile__role='restaurant',
        username__icontains=query
    ).exclude(restaurant_profile__isnull=False)[:5]
    
    for owner in matching_owners:
        # Auto-create the restaurant profile for this owner so they are findable
        Restaurant.objects.get_or_create(
            owner=owner,
            defaults={
                'name': owner.username,
                'display_name': owner.username,
                'is_active': True,
                'cuisine': 'Other',
                'borough': 'Unknown'
            }
        )
    
    # 3. Search all Restaurants (now including the newly created stubs)
    restaurant_qs = Restaurant.objects.filter(
        Q(name__icontains=query) | 
        Q(display_name__icontains=query) |
        Q(name_normalized__icontains=query) |
        Q(owner__username__icontains=query) |
        Q(address__icontains=query) |
        Q(street__icontains=query) |
        Q(building__icontains=query) |
        Q(zip_code__icontains=query) |
        Q(borough__icontains=query) |
        Q(neighborhood__icontains=query) |
        Q(cuisine__icontains=query)
    ).distinct().order_by("name")[:50]
    
    results = [{"id": r.id, "name": r.display_name or r.name} for r in restaurant_qs]
    return JsonResponse({"results": results})


@login_required
@require_GET
def diner_search_api_v2(request):
    """AJAX search for Diner users specifically for group chat creation."""
    query = request.GET.get("search", "").strip()
    if not query:
        return JsonResponse({"results": []})
    
    # Filter for diners only, exclude self
    diners = User.objects.filter(
        Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query),
        userprofile__role='diner'
    ).exclude(id=request.user.id).values('id', 'username')[:20]
    
    results = [{"id": d['id'], "username": d['username']} for d in diners]
    return JsonResponse({"results": results})


@login_required
def seed_restaurants_v2(request):
    """Temporary view to seed 5 test restaurants as requested."""
    test_names = ["Rest_A_Testing", "Rest_B_Testing", "Rest_C_Testing", "Rest_D_Testing", "Rest_E_Testing"]
    created_count = 0
    for name in test_names:
        obj, created = Restaurant.objects.get_or_create(
            name=name,
            defaults={
                'is_active': True,
                'cuisine': 'Test Cuisine',
                'borough': 'Manhattan'
            }
        )
        if created:
            created_count += 1
    return JsonResponse({"success": True, "created": created_count, "names": test_names})
