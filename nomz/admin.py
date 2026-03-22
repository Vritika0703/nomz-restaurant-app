from django.contrib import admin
from .models import (
    Restaurant,
    SystemAlert,
    SystemAuditLog,
    SystemPerformanceMetric,
    SystemPerformanceSnapshot,
)


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "neighborhood", "cuisine")
    search_fields = ("name", "neighborhood")


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
