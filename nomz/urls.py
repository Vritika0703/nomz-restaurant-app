from django.urls import path
from . import api_views, views
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("health/", views.health_check, name="health_check"),
    path(
        "signin/",
        RedirectView.as_view(pattern_name="two_factor:login", permanent=False),
        name="signin",
    ),
    path("home/", views.home, name="home"),
    path("map/", views.map_view, name="map"),
    path(
        "api/restaurants/map-data/",
        api_views.map_restaurant_data,
        name="api_restaurants_map",
    ),
    path("register/", views.register, name="register"),  # Removed <str:role>
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.dashboard, name="profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("restaurant-profile/", views.restaurant_profile, name="restaurant_profile"),
    path("search/", views.restaurant_search, name="restaurant_search"),
    path("preferences/", views.manage_preferences, name="manage_preferences"),
    # Restaurant Profile Management
    path(
        "restaurant/create/", views.create_restaurant_profile, name="create_restaurant"
    ),
    path("restaurant/edit/", views.edit_restaurant_profile, name="edit_restaurant"),
    path(
        "restaurant/availability/",
        views.manage_availability,
        name="manage_availability",
    ),
    path("restaurant/activate/", views.manage_activation, name="manage_activation"),
    # Restaurant Photo Management
    path("restaurant/photos/", views.restaurant_photos, name="restaurant_photos"),
    path("restaurant/photos/upload/", views.upload_photo, name="upload_photo"),
    path(
        "restaurant/photos/<int:photo_id>/delete/",
        views.delete_photo,
        name="delete_photo",
    ),
    path(
        "restaurant/photos/<int:photo_id>/set-primary/",
        views.set_primary_photo,
        name="set_primary_photo",
    ),
    # Password reset (Django built-in)
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
            success_url="/password-reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url="/reset/done/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    # Admin Quick Actions & Redirects (Fix for Issue #46 relative link 404)
    path("admin-login/", views.admin_login, name="admin_login"),
    path(
        "dashboard/Admin-login/",
        RedirectView.as_view(url="/admin-login/", permanent=False),
    ),
    path(
        "dashboard/admin-login/",
        RedirectView.as_view(url="/admin-login/", permanent=False),
    ),
    path("nomz-admin/logs/", views.admin_login_logs, name="admin_login_logs"),
    path("nomz-admin/users/", views.admin_manage_users, name="admin_manage_users"),
    path(
        "nomz-admin/users/<int:user_id>/toggle/",
        views.toggle_user_status,
        name="toggle_user_status",
    ),
    path(
        "dashboard-action/users/<int:user_id>/toggle/",
        views.admin_toggle_user_status,
        name="admin_toggle_user_status",
    ),
    path(
        "nomz-admin/approved-accounts/",
        views.admin_approved_accounts,
        name="admin_approved_accounts",
    ),
    path(
        "nomz-admin/rejected-accounts/",
        views.admin_rejected_accounts,
        name="admin_rejected_accounts",
    ),
    path(
        "nomz-admin/pending-approvals/",
        views.admin_pending_approvals,
        name="admin_pending_approvals",
    ),
    path(
        "nomz-admin/approve/<int:user_id>/",
        views.admin_approve_restaurant,
        name="admin_approve_restaurant",
    ),
    path(
        "nomz-admin/reject/<int:user_id>/",
        views.admin_reject_restaurant,
        name="admin_reject_restaurant",
    ),
]
