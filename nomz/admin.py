from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .scoring import refresh_restaurant_composite
from .models import (
    Restaurant,
    RestaurantOwnershipClaim,
    Review,
    SystemAlert,
    SystemAuditLog,
    SystemPerformanceMetric,
    SystemPerformanceSnapshot,
)


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "neighborhood", "cuisine")
    search_fields = ("name", "neighborhood")
    actions = ("recalculate_selected_scores",)

    @admin.action(description="Recalculate composite score for selected restaurants")
    def recalculate_selected_scores(self, request, queryset):
        refreshed = 0
        for restaurant in queryset:
            refresh_restaurant_composite(restaurant)
            refreshed += 1
        self.message_user(
            request,
            f"Recalculated composite scores for {refreshed} restaurant(s).",
            level=messages.SUCCESS,
        )


@admin.register(SystemPerformanceMetric)
class SystemPerformanceMetricAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "method",
        "path",
        "status_code",
        "duration_ms",
        "is_error",
    )
    list_filter = ("status_code", "is_error", "method")
    search_fields = ("path", "exception_class", "exception_message")
    ordering = ("-created_at",)


@admin.register(SystemPerformanceSnapshot)
class SystemPerformanceSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "interval_end",
        "interval_start",
        "total_requests",
        "error_requests",
        "error_rate",
        "avg_latency_ms",
        "max_latency_ms",
    )
    list_filter = ("interval_end",)
    ordering = ("-interval_end",)


@admin.register(SystemAlert)
class SystemAlertAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "alert_type",
        "severity",
        "is_active",
        "resolved_at",
        "message",
    )
    list_filter = ("alert_type", "severity", "is_active")
    search_fields = ("message",)
    ordering = ("-created_at",)


@admin.register(SystemAuditLog)
class SystemAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "level",
        "action",
        "actor_username",
        "request_path",
        "http_method",
    )
    list_filter = ("level", "action")
    search_fields = (
        "actor_username",
        "action",
        "request_path",
        "ip_address",
        "user_agent",
    )
    ordering = ("-created_at",)


@admin.register(RestaurantOwnershipClaim)
class RestaurantOwnershipClaimAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "restaurant",
        "claimant",
        "status",
        "created_at",
        "reviewed_at",
    )
    list_filter = ("status", "created_at", "reviewed_at")
    search_fields = (
        "restaurant__name",
        "restaurant__address",
        "claimant__username",
        "claimant__email",
        "business_email",
    )
    readonly_fields = ("created_at", "updated_at", "reviewed_at")
    actions = ("approve_selected_claims", "reject_selected_claims")

    @admin.action(description="Approve selected pending claims")
    def approve_selected_claims(self, request, queryset):
        approved_count = 0
        for claim in queryset.select_related("restaurant", "claimant"):
            if claim.status != RestaurantOwnershipClaim.STATUS_PENDING:
                continue
            try:
                claim.approve(reviewer=request.user)
                approved_count += 1
            except ValidationError as exc:
                self.message_user(
                    request,
                    f"Could not approve claim #{claim.id}: {exc}",
                    level=messages.ERROR,
                )
        self.message_user(request, f"Approved {approved_count} claim(s).")

    @admin.action(description="Reject selected pending claims")
    def reject_selected_claims(self, request, queryset):
        rejected_count = 0
        for claim in queryset:
            if claim.status != RestaurantOwnershipClaim.STATUS_PENDING:
                continue
            claim.reject(reviewer=request.user, notes="Rejected via admin bulk action.")
            rejected_count += 1
        self.message_user(request, f"Rejected {rejected_count} claim(s).")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "restaurant",
        "user",
        "rating",
        "food_quality_rating",
        "service_quality_rating",
        "ambience_rating",
        "location_rating",
        "value_rating",
        "created_at",
        "is_flagged",
        "is_deleted",
    )
    list_filter = ("is_flagged", "is_deleted", "created_at")
    search_fields = ("restaurant__name", "user__username", "comment")
    ordering = ("-created_at",)
