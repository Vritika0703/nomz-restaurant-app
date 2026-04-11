from django.urls import path
from . import api_views, spa_api, views
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
    path(
        "api/messages/conversations/",
        api_views.list_conversations,
        name="api_conversation_list",
    ),
    path(
        "api/messages/conversations/start/",
        api_views.start_conversation,
        name="api_conversation_start",
    ),
    path(
        "api/messages/conversations/<int:conversation_id>/",
        api_views.conversation_messages,
        name="api_conversation_messages",
    ),
    path(
        "api/messages/conversations/<int:conversation_id>/send/",
        api_views.send_message,
        name="api_send_message",
    ),
    path(
        "api/restaurant-claim/",
        api_views.restaurant_claim_api,
        name="api_restaurant_claim",
    ),
    path("api/auth/session/", spa_api.auth_session, name="api_auth_session"),
    path("api/auth/register/", spa_api.auth_register, name="api_auth_register"),
    path("api/auth/login/", spa_api.auth_login, name="api_auth_login"),
    path("api/auth/admin-login/", spa_api.auth_admin_login, name="api_auth_admin_login"),
    path("api/auth/logout/", spa_api.auth_logout, name="api_auth_logout"),
    path("api/auth/2fa/verify/", spa_api.auth_2fa_verify, name="api_auth_2fa_verify"),
    path(
        "api/auth/password-reset/",
        spa_api.auth_password_reset_request,
        name="api_auth_password_reset",
    ),
    path(
        "api/auth/password-reset/confirm/",
        spa_api.auth_password_reset_confirm,
        name="api_auth_password_reset_confirm",
    ),
    path(
        "api/restaurant/photos/data/",
        spa_api.restaurant_photos_data,
        name="api_restaurant_photos_data",
    ),
    path(
        "api/restaurant/photos/upload/",
        spa_api.restaurant_photo_upload,
        name="api_restaurant_photo_upload",
    ),
    path(
        "api/restaurant/photos/<int:photo_id>/delete/",
        spa_api.restaurant_photo_delete,
        name="api_restaurant_photo_delete",
    ),
    path(
        "api/restaurant/photos/<int:photo_id>/set-primary/",
        spa_api.restaurant_photo_set_primary,
        name="api_restaurant_photo_set_primary",
    ),
    path(
        "api/restaurant/activation/",
        spa_api.restaurant_activation_api,
        name="api_restaurant_activation",
    ),
    path(
        "api/diner/preferences/",
        spa_api.diner_preferences_api,
        name="api_diner_preferences",
    ),
    path(
        "api/diner/account/",
        spa_api.diner_account_api,
        name="api_diner_account",
    ),
    path(
        "api/admin/dashboard-summary/",
        spa_api.admin_dashboard_summary,
        name="api_admin_dashboard_summary",
    ),
    path(
        "api/admin/pending-approvals/",
        spa_api.admin_pending_approvals_data,
        name="api_admin_pending_approvals_data",
    ),
    path(
        "api/admin/approved-restaurants/",
        spa_api.admin_approved_restaurant_accounts_data,
        name="api_admin_approved_restaurants",
    ),
    path(
        "api/admin/rejected-restaurants/",
        spa_api.admin_rejected_restaurant_accounts_data,
        name="api_admin_rejected_restaurants",
    ),
    path(
        "api/admin/approve/<int:user_id>/",
        spa_api.admin_approve_user_api,
        name="api_admin_approve_user",
    ),
    path(
        "api/admin/reject/<int:user_id>/",
        spa_api.admin_reject_user_api,
        name="api_admin_reject_user",
    ),
    path(
        "api/admin/moderation/",
        spa_api.admin_moderation_data,
        name="api_admin_moderation_data",
    ),
    path(
        "api/admin/moderation/reports/<int:report_id>/resolve/",
        spa_api.admin_resolve_report_api,
        name="api_admin_resolve_report_api",
    ),
    path(
        "api/admin/users/",
        spa_api.admin_users_data,
        name="api_admin_users_data",
    ),
    path(
        "api/admin/users/<int:user_id>/toggle-active/",
        spa_api.admin_toggle_user_active_api,
        name="api_admin_toggle_user_active",
    ),
    path(
        "api/admin/login-logs/",
        spa_api.admin_login_logs_data,
        name="api_admin_login_logs_data",
    ),
    path(
        "api/restaurants/<int:restaurant_id>/",
        spa_api.restaurant_detail_data,
        name="api_restaurant_detail",
    ),
    path(
        "api/restaurants/<int:restaurant_id>/review/",
        spa_api.restaurant_add_review,
        name="api_restaurant_add_review",
    ),
    path(
        "api/report/",
        spa_api.report_content_api,
        name="api_report_content",
    ),
    path("api/search/", spa_api.restaurant_search_api, name="api_restaurant_search"),
    path(
        "api/recommendations/",
        spa_api.diner_recommendations_api,
        name="api_diner_recommendations",
    ),
    path(
        "api/restaurant/profile/",
        spa_api.restaurant_profile_api,
        name="api_restaurant_profile",
    ),
    path(
        "api/restaurant/availability/",
        spa_api.restaurant_availability_api,
        name="api_restaurant_availability",
    ),
    path(
        "api/restaurant/communication/",
        spa_api.restaurant_communication_api,
        name="api_restaurant_communication",
    ),
    path("register/", views.register, name="register"),  # Removed <str:role>
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.dashboard, name="profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "dashboard/search/",
        RedirectView.as_view(url="/search/", permanent=False),
        name="restaurant_search_dashboard_alias",
    ),
    path("restaurant-profile/", views.restaurant_profile, name="restaurant_profile"),
    path("search/", views.restaurant_search, name="restaurant_search"),
    path("preferences/", views.manage_preferences, name="manage_preferences"),
    path("recommendations/", views.recommendations, name="recommendations"),
    # Restaurant Profile Management
    path("restaurant/claim/", views.claim_restaurant, name="claim_restaurant"),
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
    path(
        "restaurant/communication/",
        views.manage_communication_settings,
        name="manage_communication_settings",
    ),
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
    # Moderation & Reviews
    path(
        "restaurant/<int:restaurant_id>/",
        views.restaurant_detail,
        name="restaurant_detail",
    ),
    path("messages/", views.message_inbox, name="message_inbox"),
    path(
        "messages/restaurant/<int:restaurant_id>/",
        views.message_restaurant,
        name="message_restaurant",
    ),
    path(
        "messages/conversations/<int:conversation_id>/",
        views.conversation_detail,
        name="conversation_detail",
    ),
    path(
        "restaurant/<int:restaurant_id>/review/",
        views.add_review,
        name="add_review",
    ),
    path(
        "report/<str:content_type>/<int:content_id>/",
        views.report_content,
        name="report_content",
    ),
    path(
        "nomz-admin/moderation/",
        views.admin_moderation_dashboard,
        name="admin_moderation_dashboard",
    ),
    path(
        "nomz-admin/moderation/resolve/<int:report_id>/",
        views.admin_resolve_report,
        name="admin_resolve_report",
    ),
]
