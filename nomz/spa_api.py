"""
JSON endpoints for the React SPA (session auth, photos, admin summaries).
Uses session cookies + @csrf_exempt on mutating POSTs (same pattern as api_views).
"""
from __future__ import annotations

import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods
from django.utils import timezone
from django_otp import user_has_device, match_token

from django.contrib.auth.decorators import login_required

from .forms import (
    RestaurantActivationForm,
    RestaurantPhotoForm,
    UserPreferenceForm,
    UserRegisterForm,
    ReviewForm,
    ModerationReportForm,
)
from .models import (
    LoginLog,
    ModerationReport,
    Restaurant,
    RestaurantOwnershipClaim,
    RestaurantPhoto,
    Review,
    UserPreference,
    UserProfile,
)

from .api_views import (  # reuse helpers
    _is_diner,
    _is_restaurant_owner,
    _json_error,
)


def _staff_json_required(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return _json_error("Staff access required.", status=403)
    return None


def session_payload(request) -> dict:
    if not request.user.is_authenticated:
        return {"authenticated": False}
    u = request.user
    role = None
    profile_data = None
    if hasattr(u, "userprofile"):
        role = u.userprofile.role
        profile_data = {
            "is_approved": u.userprofile.is_approved,
            "is_rejected": u.userprofile.is_rejected,
            "role": u.userprofile.role,
        }
    return {
        "authenticated": True,
        "user_id": u.id,
        "username": u.username,
        "email": u.email or "",
        "role": role,
        "is_staff": u.is_staff,
        "is_superuser": u.is_superuser,
        "userprofile": profile_data,
    }


@require_http_methods(["GET", "HEAD"])
def auth_session(request):
    return JsonResponse(session_payload(request))


@csrf_exempt
@require_http_methods(["POST"])
def auth_register(request):
    if request.user.is_authenticated:
        return JsonResponse(session_payload(request))

    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return _json_error("Invalid JSON.")

    form = UserRegisterForm(
        {
            "email": body.get("email", ""),
            "username": body.get("username", ""),
            "role": body.get("role", ""),
            "password1": body.get("password1", ""),
            "password2": body.get("password2", ""),
        }
    )
    if form.is_valid():
        user = form.save()
        login(request, user)
        return JsonResponse(session_payload(request), status=201)

    errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
    return JsonResponse({"success": False, "errors": errors}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def auth_login(request):
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return _json_error("Invalid JSON.")

    username = (body.get("username") or "").strip()
    password = body.get("password") or ""
    if not username or not password:
        return _json_error("Username and password are required.")

    form = AuthenticationForm(
        request,
        data={"username": username, "password": password},
    )
    if form.is_valid():
        user = form.get_user()
        # Check if user has a confirmed 2FA device
        if user_has_device(user, confirmed=True):
            request.session["_2fa_user_id"] = user.id
            return JsonResponse({"requires_2fa": True, "authenticated": False})
        login(request, user)
        return JsonResponse(session_payload(request))

    err_msg = "Invalid username or password."
    if form.errors.get("__all__"):
        err_msg = "; ".join(str(e) for e in form.errors["__all__"])
    return _json_error(err_msg, status=401)


@csrf_exempt
@require_http_methods(["POST"])
def auth_2fa_verify(request):
    """Verify a 2FA token for a pending login."""
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return _json_error("Invalid JSON.")

    user_id = request.session.get("_2fa_user_id")
    if not user_id:
        return _json_error("No pending two-factor authentication.", status=400)

    token = (body.get("token") or "").strip()
    if not token:
        return _json_error("Authentication code is required.")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return _json_error("Invalid session.", status=400)

    device = match_token(user, token)
    if device is not None:
        del request.session["_2fa_user_id"]
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return JsonResponse(session_payload(request))

    return _json_error("Invalid authentication code.", status=401)


@csrf_exempt
@require_http_methods(["POST"])
def auth_logout(request):
    logout(request)
    return JsonResponse({"authenticated": False})


@csrf_exempt
@require_http_methods(["POST"])
def auth_password_reset_request(request):
    """Send a password-reset email (SPA flow)."""
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return _json_error("Invalid JSON.")

    email = (body.get("email") or "").strip()
    if not email:
        return _json_error("Email is required.")

    form = PasswordResetForm({"email": email})
    if form.is_valid():
        form.save(
            request=request,
            use_https=request.is_secure(),
            email_template_name="registration/password_reset_email_spa.html",
            subject_template_name="registration/password_reset_subject.txt",
        )
    # Always return success to prevent email enumeration
    return JsonResponse({"success": True})


@csrf_exempt
@require_http_methods(["POST"])
def auth_password_reset_confirm(request):
    """Validate uid/token and set a new password (SPA flow)."""
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return _json_error("Invalid JSON.")

    uid = body.get("uid", "")
    token = body.get("token", "")
    new_password1 = body.get("new_password1", "")
    new_password2 = body.get("new_password2", "")

    if not uid or not token:
        return _json_error("Invalid reset link.", status=400)
    if not new_password1 or not new_password2:
        return _json_error("Both password fields are required.", status=400)

    try:
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return _json_error("Invalid reset link.", status=400)

    if not default_token_generator.check_token(user, token):
        return JsonResponse(
            {"success": False, "expired": True, "error": "Reset link has expired or is invalid."},
            status=400,
        )

    form = SetPasswordForm(user, {"new_password1": new_password1, "new_password2": new_password2})
    if form.is_valid():
        form.save()
        return JsonResponse({"success": True})

    errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
    return JsonResponse({"success": False, "errors": errors}, status=400)


# --- Restaurant photos ---


@login_required(login_url="landing")
@require_GET
def restaurant_photos_data(request):

    if not _is_restaurant_owner(request.user):
        return _json_error("Restaurant owners only.", status=403)

    restaurant = Restaurant.objects.filter(owner=request.user).first()
    if not restaurant:
        return JsonResponse({"restaurant_id": None, "photos": []})

    photos = []
    for p in restaurant.photos.all():
        url = ""
        if p.photo:
            try:
                url = request.build_absolute_uri(p.photo.url)
            except Exception:
                url = p.photo.url
        photos.append(
            {
                "id": p.id,
                "url": url,
                "caption": p.caption or "",
                "is_primary": p.is_primary,
            }
        )
    return JsonResponse({"restaurant_id": restaurant.id, "photos": photos})


@csrf_exempt
@login_required(login_url="landing")
@require_http_methods(["POST"])
def restaurant_photo_upload(request):

    if not _is_restaurant_owner(request.user):
        return HttpResponseForbidden("Restaurant owners only.")

    restaurant = get_object_or_404(Restaurant, owner=request.user)
    form = RestaurantPhotoForm(request.POST, request.FILES)
    if form.is_valid():
        photo = form.save(commit=False)
        photo.restaurant = restaurant
        photo.save()
        url = ""
        if photo.photo:
            try:
                url = request.build_absolute_uri(photo.photo.url)
            except Exception:
                url = photo.photo.url
        return JsonResponse(
            {
                "id": photo.id,
                "url": url,
                "caption": photo.caption or "",
                "is_primary": photo.is_primary,
            },
            status=201,
        )
    errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
    return JsonResponse({"errors": errors}, status=400)


@csrf_exempt
@login_required(login_url="landing")
@require_http_methods(["POST"])
def restaurant_photo_delete(request, photo_id):

    if not _is_restaurant_owner(request.user):
        return HttpResponseForbidden("Restaurant owners only.")

    photo = get_object_or_404(RestaurantPhoto, id=photo_id)
    if photo.restaurant.owner_id != request.user.id:
        return HttpResponseForbidden("Permission denied.")

    photo.delete()
    return JsonResponse({"ok": True})


@csrf_exempt
@login_required(login_url="landing")
@require_http_methods(["POST"])
def restaurant_photo_set_primary(request, photo_id):

    if not _is_restaurant_owner(request.user):
        return HttpResponseForbidden("Restaurant owners only.")

    photo = get_object_or_404(RestaurantPhoto, id=photo_id)
    if photo.restaurant.owner_id != request.user.id:
        return HttpResponseForbidden("Permission denied.")

    photo.is_primary = True
    photo.save()
    return JsonResponse({"ok": True})


# --- Profile activation ---


@csrf_exempt
@login_required(login_url="landing")
@require_http_methods(["GET", "POST"])
def restaurant_activation_api(request):

    if not _is_restaurant_owner(request.user):
        return _json_error("Restaurant owners only.", status=403)

    restaurant = get_object_or_404(Restaurant, owner=request.user)

    if request.method == "GET":
        return JsonResponse({"is_active": restaurant.is_active})

    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return _json_error("Invalid JSON.")

    if "is_active" not in body:
        return _json_error("is_active is required.")

    form = RestaurantActivationForm({"is_active": bool(body["is_active"])}, instance=restaurant)
    if form.is_valid():
        form.save()
        return JsonResponse({"is_active": restaurant.is_active})
    errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
    return JsonResponse({"errors": errors}, status=400)


# --- Diner preferences ---


@csrf_exempt
@login_required(login_url="landing")
@require_http_methods(["GET", "POST"])
def diner_preferences_api(request):

    if not _is_diner(request.user):
        return _json_error("Diners only.", status=403)

    preferences, _ = UserPreference.objects.get_or_create(user=request.user)

    if request.method == "GET":
        return JsonResponse(
            {
                "favorite_cuisines": preferences.favorite_cuisines or [],
                "dietary_restrictions": preferences.dietary_restrictions or [],
                "price_preference": preferences.price_preference or "",
                "neighborhood_preference": preferences.neighborhood_preference or "",
            }
        )

    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return _json_error("Invalid JSON.")

    form = UserPreferenceForm(body, instance=preferences)
    if form.is_valid():
        form.save()
        return JsonResponse({"success": True})

    errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
    return JsonResponse({"errors": errors}, status=400)


# --- Admin JSON ---


@login_required(login_url="landing")
@require_GET
def admin_dashboard_summary(request):

    deny = _staff_json_required(request)
    if deny:
        return deny

    diner_count = UserProfile.objects.filter(role="diner").count()
    restaurant_count = Restaurant.objects.count()
    pending_approval_count = UserProfile.objects.filter(
        role="restaurant", is_approved=False, is_rejected=False
    ).count()
    approved_business_count = UserProfile.objects.filter(
        role="restaurant", is_approved=True
    ).count()
    rejected_business_count = UserProfile.objects.filter(
        role="restaurant", is_rejected=True
    ).count()
    pending_report_count = ModerationReport.objects.filter(status="PENDING").count()
    suspicious_count = LoginLog.objects.filter(is_suspicious=True).count()
    flagged_content = (
        Review.objects.filter(is_flagged=True).count()
        + Restaurant.objects.filter(is_flagged=True).count()
    )

    return JsonResponse(
        {
            "total_users": User.objects.count(),
            "total_restaurants": restaurant_count,
            "diner_count": diner_count,
            "pending_approvals": pending_approval_count,
            "approved_business_count": approved_business_count,
            "rejected_business_count": rejected_business_count,
            "pending_reports": pending_report_count,
            "suspicious_accounts": suspicious_count,
            "flagged_content": flagged_content,
        }
    )


@login_required(login_url="landing")
@require_GET
def admin_pending_approvals_data(request):

    deny = _staff_json_required(request)
    if deny:
        return deny

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
    claims_by_user_id = {c.claimant_id: c for c in pending_claims}

    results = []
    for u in pending_approvals:
        claim = claims_by_user_id.get(u.id)
        results.append(
            {
                "id": u.id,
                "username": u.username,
                "email": u.email or "",
                "date_joined": u.date_joined.isoformat(),
                "restaurant_name": claim.restaurant.name if claim else "",
                "business_email": (claim.business_email if claim else "") or "",
                "claim_details": (claim.proof_details if claim else "") or "",
                "has_pending_claim": claim is not None,
            }
        )

    return JsonResponse({"count": len(results), "results": results})


@csrf_exempt
@login_required(login_url="landing")
@require_http_methods(["POST"])
def admin_approve_user_api(request, user_id):

    deny = _staff_json_required(request)
    if deny:
        return deny

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
                notes="Approved via SPA admin API.",
            )
        except ValidationError as exc:
            return _json_error(str(exc), status=400)

    if hasattr(user_to_approve, "userprofile"):
        profile = user_to_approve.userprofile
        profile.is_approved = True
        profile.is_rejected = False
        profile.save()

    return JsonResponse({"ok": True})


@csrf_exempt
@login_required(login_url="landing")
@require_http_methods(["POST"])
def admin_reject_user_api(request, user_id):

    deny = _staff_json_required(request)
    if deny:
        return deny

    user_to_reject = get_object_or_404(User, id=user_id)

    pending_claims = RestaurantOwnershipClaim.objects.filter(
        claimant=user_to_reject,
        status=RestaurantOwnershipClaim.STATUS_PENDING,
    )
    for claim in pending_claims:
        claim.reject(
            reviewer=request.user,
            notes="Rejected via SPA admin API.",
        )

    if hasattr(user_to_reject, "userprofile"):
        profile = user_to_reject.userprofile
        profile.is_approved = False
        profile.is_rejected = True
        profile.save()

    return JsonResponse({"ok": True})


@login_required(login_url="landing")
@require_GET
def admin_moderation_data(request):

    deny = _staff_json_required(request)
    if deny:
        return deny

    pending = ModerationReport.objects.filter(status="PENDING").order_by("-created_at")
    resolved = (
        ModerationReport.objects.exclude(status="PENDING")
        .order_by("-created_at")[:25]
    )

    def row(r: ModerationReport):
        return {
            "id": r.id,
            "reason": r.reason,
            "details": r.details,
            "status": r.status,
            "reporter_username": r.reporter.username,
            "created_at": r.created_at.isoformat(),
            "review_id": r.review_id,
            "reported_user_id": r.reported_user_id,
        }

    return JsonResponse(
        {
            "pending": [row(r) for r in pending],
            "resolved": [row(r) for r in resolved],
        }
    )


@csrf_exempt
@login_required(login_url="landing")
@require_http_methods(["POST"])
def admin_resolve_report_api(request, report_id):

    deny = _staff_json_required(request)
    if deny:
        return deny

    report = get_object_or_404(ModerationReport, id=report_id)
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return _json_error("Invalid JSON.")

    action = (body.get("action") or "").strip()
    moderator_note = (body.get("moderator_note") or "").strip()

    if action == "dismiss":
        report.status = "DISMISSED"
        report.action_taken = "No action taken"
    elif action == "flag_fraud":
        if report.review:
            report.review.is_flagged = True
            report.review.save()
            report.action_taken = "Review flagged as fraudulent"
        elif report.reported_user:
            if hasattr(report.reported_user, "userprofile"):
                report.reported_user.userprofile.is_flagged = True
                report.reported_user.userprofile.save()
            Restaurant.objects.filter(owner=report.reported_user).update(is_flagged=True)
            report.action_taken = "User and associated restaurant(s) flagged for fraud"
        report.status = "RESOLVED"
    elif action == "unflag":
        if report.review:
            report.review.is_flagged = False
            report.review.save()
            report.action_taken = "Review un-flagged"
        elif report.reported_user:
            if hasattr(report.reported_user, "userprofile"):
                report.reported_user.userprofile.is_flagged = False
                report.reported_user.userprofile.save()
            Restaurant.objects.filter(owner=report.reported_user).update(is_flagged=False)
            report.action_taken = "User and associated restaurant(s) un-flagged"
        report.status = "PENDING"
    else:
        return _json_error("Invalid action.", status=400)

    report.moderator_note = moderator_note
    report.resolved_at = timezone.now()
    report.save()
    return JsonResponse({"ok": True})


@login_required(login_url="landing")
@require_GET
def admin_users_data(request):

    deny = _staff_json_required(request)
    if deny:
        return deny

    users = (
        User.objects.all()
        .exclude(pk=request.user.pk)
        .select_related("userprofile")
        .order_by("-date_joined")
    )
    from django.db.models import Exists, OuterRef

    suspicious_logs = LoginLog.objects.filter(
        username=OuterRef("username"), is_user_suspicious=True
    )
    users = users.annotate(has_suspicious_activity=Exists(suspicious_logs))

    payload = []
    for u in users:
        role = getattr(u.userprofile, "role", None) if hasattr(u, "userprofile") else None
        payload.append(
            {
                "id": u.id,
                "username": u.username,
                "email": u.email or "",
                "is_active": u.is_active,
                "is_superuser": u.is_superuser,
                "date_joined": u.date_joined.isoformat(),
                "role": role,
                "has_suspicious_activity": getattr(
                    u, "has_suspicious_activity", False
                ),
            }
        )
    return JsonResponse({"count": len(payload), "results": payload})


@csrf_exempt
@login_required(login_url="landing")
@require_http_methods(["POST"])
def admin_toggle_user_active_api(request, user_id):

    deny = _staff_json_required(request)
    if deny:
        return deny

    user_to_toggle = get_object_or_404(User, id=user_id)
    if user_to_toggle.is_superuser:
        return _json_error("Cannot toggle superuser.", status=400)
    if user_to_toggle == request.user:
        return _json_error("Cannot toggle yourself.", status=400)

    user_to_toggle.is_active = not user_to_toggle.is_active
    user_to_toggle.save()
    return JsonResponse({"ok": True, "is_active": user_to_toggle.is_active})


@login_required(login_url="landing")
@require_GET
def admin_login_logs_data(request):

    deny = _staff_json_required(request)
    if deny:
        return deny

    logs = LoginLog.objects.all().order_by("-timestamp")[:200]
    payload = [
        {
            "id": log.id,
            "username": log.username,
            "status": log.status,
            "timestamp": log.timestamp.isoformat(),
            "ip_address": log.ip_address or "",
            "is_suspicious": log.is_suspicious,
            "is_user_suspicious": log.is_user_suspicious,
        }
        for log in logs
    ]
    return JsonResponse({"count": len(payload), "results": payload})


# ── Restaurant detail, reviews, reports (SPA) ──────────────────────


@require_GET
def restaurant_detail_data(request, restaurant_id):
    """Return JSON detail for a single restaurant + its reviews."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    is_owner_flagged = False
    owner_id = None
    messaging_enabled = restaurant.messaging_enabled
    if restaurant.owner:
        owner_id = restaurant.owner.id
        if hasattr(restaurant.owner, "userprofile"):
            is_owner_flagged = getattr(
                restaurant.owner.userprofile, "is_flagged", False
            )

    reviews_qs = restaurant.reviews.filter(is_deleted=False).order_by("-created_at")
    reviews_list = []
    for r in reviews_qs:
        reviews_list.append(
            {
                "id": r.id,
                "username": r.user.username,
                "rating": r.rating,
                "food_quality_rating": r.food_quality_rating,
                "service_quality_rating": r.service_quality_rating,
                "ambience_rating": r.ambience_rating,
                "location_rating": r.location_rating,
                "value_rating": r.value_rating,
                "dietary_accommodation_rating": r.dietary_accommodation_rating,
                "cleanliness_rating": r.cleanliness_rating,
                "comment": r.comment or "",
                "created_at": r.created_at.isoformat(),
                "is_flagged": r.is_flagged,
            }
        )

    data = {
        "id": restaurant.id,
        "name": restaurant.display_name or restaurant.name,
        "cuisine": restaurant.cuisine or "",
        "cuisine_tags": restaurant.cuisine_tags or [],
        "neighborhood": restaurant.neighborhood or "",
        "address": ", ".join(
            p
            for p in [
                restaurant.building or "",
                restaurant.street or "",
                restaurant.borough or "",
                restaurant.zip_code or "",
            ]
            if p
        ),
        "description": restaurant.description or "",
        "phone": restaurant.phone or "",
        "is_flagged": restaurant.is_flagged,
        "is_owner_flagged": is_owner_flagged,
        "owner_id": owner_id,
        "messaging_enabled": messaging_enabled,
        "composite_score": float(restaurant.composite_score)
        if restaurant.composite_score is not None
        else None,
        "grade": restaurant.grade_latest or "",
        "reviews": reviews_list,
    }
    return JsonResponse(data)


@csrf_exempt
@login_required(login_url="landing")
@require_http_methods(["POST"])
def restaurant_add_review(request, restaurant_id):
    """Submit a review for a restaurant (JSON)."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return _json_error("Invalid JSON.")

    form = ReviewForm(body)
    if form.is_valid():
        review = form.save(commit=False)
        review.restaurant = restaurant
        review.user = request.user
        review.save()
        return JsonResponse(
            {
                "success": True,
                "review_id": review.id,
            },
            status=201,
        )

    errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
    return JsonResponse({"success": False, "errors": errors}, status=400)


@csrf_exempt
@login_required(login_url="landing")
@require_http_methods(["POST"])
def report_content_api(request):
    """Report a review or user (JSON)."""
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return _json_error("Invalid JSON.")

    content_type = body.get("content_type", "")
    content_id = body.get("content_id")

    if content_type not in ("review", "user") or not content_id:
        return _json_error("Invalid report target.", status=400)

    review = None
    reported_user = None

    if content_type == "review":
        try:
            review = Review.objects.get(id=content_id)
        except Review.DoesNotExist:
            return _json_error("Review not found.", status=404)
    else:
        from django.contrib.auth.models import User as AuthUser

        try:
            reported_user = AuthUser.objects.get(id=content_id)
        except AuthUser.DoesNotExist:
            return _json_error("User not found.", status=404)

    form = ModerationReportForm(
        {"reason": body.get("reason", ""), "details": body.get("details", "")}
    )
    if form.is_valid():
        report = form.save(commit=False)
        report.reporter = request.user
        report.review = review
        report.reported_user = reported_user
        report.save()
        return JsonResponse({"success": True, "report_id": report.id}, status=201)

    errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
    return JsonResponse({"success": False, "errors": errors}, status=400)
