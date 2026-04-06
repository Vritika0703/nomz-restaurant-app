from __future__ import annotations

import json
from decimal import Decimal

from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Conversation, Message, MessageNotification, Restaurant
from .restaurant_sorting import normalize_sort_key, sort_restaurant_queryset

NYC_MIN_LAT = 40.0
NYC_MAX_LAT = 41.5
NYC_MIN_LON = -75.5
NYC_MAX_LON = -72.0


def _safe_decimal_to_float(value: Decimal | None) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_score_text(value: Decimal | None) -> str:
    if value is None:
        return "No score"
    number = _safe_decimal_to_float(value)
    if number is None:
        return "No score"
    return f"{number:.0f}" if number.is_integer() else f"{number:.1f}"


def _coerce_float(raw_value: str) -> float | None:
    try:
        return float(raw_value)
    except (TypeError, ValueError):
        return None


@require_GET
def map_restaurant_data(request):
    """
    Return restaurant marker-ready JSON for the map UI.
    """
    queryset = Restaurant.objects.filter(
        Q(owner__userprofile__is_approved=True) | Q(owner__isnull=True),
        is_active=True,
        latitude__isnull=False,
        longitude__isnull=False,
        latitude__gte=NYC_MIN_LAT,
        latitude__lte=NYC_MAX_LAT,
        longitude__gte=NYC_MIN_LON,
        longitude__lte=NYC_MAX_LON,
    ).select_related("owner")

    search = request.GET.get("search", "").strip()
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search)
            | Q(street__icontains=search)
            | Q(zip_code__icontains=search)
            | Q(borough__iexact=search)
            | Q(cuisine_tags__icontains=search)
        )

    borough = request.GET.get("borough", "").strip()
    if borough:
        queryset = queryset.filter(borough__iexact=borough)

    cuisine = request.GET.get("cuisine", "").strip()
    if cuisine:
        queryset = queryset.filter(cuisine_tags__icontains=cuisine)

    min_score_raw = request.GET.get("min_score", "").strip()
    if min_score_raw:
        min_score = _coerce_float(min_score_raw)
        if min_score is not None:
            queryset = queryset.filter(composite_score__gte=min_score)

    max_score_raw = request.GET.get("max_score", "").strip()
    if max_score_raw:
        max_score = _coerce_float(max_score_raw)
        if max_score is not None:
            queryset = queryset.filter(composite_score__lte=max_score)

    sw_lat = _coerce_float(request.GET.get("sw_lat", "").strip())
    ne_lat = _coerce_float(request.GET.get("ne_lat", "").strip())
    sw_lng = _coerce_float(request.GET.get("sw_lng", "").strip())
    ne_lng = _coerce_float(request.GET.get("ne_lng", "").strip())
    if all(v is not None for v in (sw_lat, ne_lat, sw_lng, ne_lng)):
        queryset = queryset.filter(
            latitude__gte=sw_lat,
            latitude__lte=ne_lat,
            longitude__gte=sw_lng,
            longitude__lte=ne_lng,
        )

    limit_raw = request.GET.get("limit", "").strip()
    try:
        limit = max(1, min(int(limit_raw), 4000))
    except (TypeError, ValueError):
        limit = 1000

    sort_by = normalize_sort_key(request.GET.get("sort_by", "composite_desc"))
    queryset = sort_restaurant_queryset(queryset, sort_by)[:limit]

    points = []
    for restaurant in queryset:
        lat = _safe_decimal_to_float(restaurant.latitude)
        lon = _safe_decimal_to_float(restaurant.longitude)
        if lat is None or lon is None:
            continue

        points.append(
            {
                "id": restaurant.id,
                "name": restaurant.display_name or restaurant.name,
                "address": ", ".join(
                    part
                    for part in [
                        restaurant.building or "",
                        restaurant.street or "",
                        restaurant.borough or "",
                        restaurant.zip_code or "",
                    ]
                    if part
                ),
                "borough": restaurant.borough,
                "zip_code": restaurant.zip_code,
                "phone": restaurant.phone,
                "cuisine_tags": restaurant.cuisine_tags or [],
                "latitude": lat,
                "longitude": lon,
                "composite_score": _safe_decimal_to_float(restaurant.composite_score),
                "composite_score_label": _safe_score_text(restaurant.composite_score),
                "grade": restaurant.grade_latest or "",
                "inspected_on": (
                    restaurant.last_inspection_date.isoformat()
                    if restaurant.last_inspection_date
                    else ""
                ),
            }
        )

    return JsonResponse({"count": len(points), "results": points})


def _is_restaurant_owner(user):
    if not user or not user.is_authenticated:
        return False
    if not hasattr(user, "userprofile"):
        return False
    return user.userprofile.role == "restaurant"


def _is_diner(user):
    if not user or not user.is_authenticated:
        return False
    if not hasattr(user, "userprofile"):
        return False
    return user.userprofile.role == "diner"


def _json_error(message, status=400):
    return JsonResponse({"error": message}, status=status)


@login_required(login_url="landing")
@require_GET
def list_conversations(request):
    user = request.user

    if _is_restaurant_owner(user):
        queryset = (
            Conversation.objects.filter(restaurant__owner=user)
            .select_related("restaurant", "diner")
            .prefetch_related("messages")
            .order_by("-updated_at")
        )
    else:
        queryset = (
            Conversation.objects.filter(diner=user)
            .select_related("restaurant", "diner")
            .prefetch_related("messages")
            .order_by("-updated_at")
        )

    payload = []
    for conversation in queryset:
        last_message = conversation.messages.order_by("-created_at").first()
        payload.append(
            {
                "id": conversation.id,
                "restaurant_id": conversation.restaurant_id,
                "restaurant_name": conversation.restaurant.name,
                "diner_id": conversation.diner_id,
                "diner_username": conversation.diner.username,
                "updated_at": conversation.updated_at.isoformat(),
                "last_message": (
                    {
                        "id": last_message.id,
                        "sender_id": last_message.sender_id,
                        "body": last_message.body,
                        "created_at": last_message.created_at.isoformat(),
                    }
                    if last_message
                    else None
                ),
            }
        )

    return JsonResponse({"count": len(payload), "results": payload})


@login_required(login_url="landing")
@require_GET
def conversation_messages(request, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.select_related("restaurant", "diner", "restaurant__owner"),
        id=conversation_id,
    )

    if not conversation.can_access(request.user):
        return HttpResponseForbidden("Permission denied")

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

    messages = list(
        conversation.messages.select_related("sender")
        .order_by("created_at")
        .values("id", "sender_id", "sender__username", "body", "created_at")
    )
    serialized_messages = [
        {
            "id": row["id"],
            "sender_id": row["sender_id"],
            "sender_username": row["sender__username"],
            "body": row["body"],
            "created_at": row["created_at"].isoformat(),
        }
        for row in messages
    ]
    return JsonResponse(
        {
            "id": conversation.id,
            "restaurant_id": conversation.restaurant_id,
            "restaurant_name": conversation.restaurant.name,
            "diner_id": conversation.diner_id,
            "diner_username": conversation.diner.username,
            "messages": serialized_messages,
        }
    )


@csrf_exempt
@login_required(login_url="landing")
def start_conversation(request):
    if request.method != "POST":
        return _json_error("Method not allowed.", status=405)

    if not _is_diner(request.user):
        return HttpResponseForbidden("Only diners can start conversations.")

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return _json_error("Invalid JSON payload.")

    restaurant_id = payload.get("restaurant_id")
    first_message = (payload.get("message") or "").strip()
    if not restaurant_id:
        return _json_error("restaurant_id is required.")
    if not first_message:
        return _json_error("message is required.")

    restaurant = get_object_or_404(
        Restaurant.objects.select_related("owner"),
        id=restaurant_id,
    )
    if not restaurant.owner_id:
        return _json_error(
            "Restaurant must have an owner to receive messages.", status=400
        )

    # Issue #62: respect the restaurant's messaging toggle
    if not restaurant.messaging_enabled:
        return _json_error(
            "This restaurant has messaging disabled and is not accepting messages.",
            status=403,
        )

    conversation, _ = Conversation.objects.get_or_create(
        restaurant=restaurant,
        diner=request.user,
    )
    Message.objects.create(
        conversation=conversation,
        sender=request.user,
        body=first_message,
    )
    conversation.save(update_fields=["updated_at"])
    return JsonResponse(
        {"conversation_id": conversation.id, "created": True}, status=201
    )


@csrf_exempt
@login_required(login_url="landing")
def send_message(request, conversation_id):
    if request.method != "POST":
        return _json_error("Method not allowed.", status=405)

    conversation = get_object_or_404(
        Conversation.objects.select_related("restaurant", "restaurant__owner", "diner"),
        id=conversation_id,
    )
    if not conversation.can_access(request.user):
        return HttpResponseForbidden("Permission denied")

    if request.user.id == conversation.restaurant.owner_id:
        if not _is_restaurant_owner(request.user):
            return HttpResponseForbidden(
                "Only restaurant owners can send as restaurant."
            )
    elif request.user.id == conversation.diner_id:
        if not _is_diner(request.user):
            return HttpResponseForbidden("Only diners can send as diner.")

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return _json_error("Invalid JSON payload.")

    body = (payload.get("message") or "").strip()
    if not body:
        return _json_error("message is required.")

    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        body=body,
    )
    Conversation.objects.filter(id=conversation.id).update(
        updated_at=message.created_at
    )

    return JsonResponse(
        {
            "id": message.id,
            "conversation_id": conversation.id,
            "sender_id": message.sender_id,
            "body": message.body,
            "created_at": message.created_at.isoformat(),
        },
        status=201,
    )
