"""
URL configuration for restaurants project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from two_factor.urls import urlpatterns as tf_urls
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from nomz.spa_shell_views import spa_index

urlpatterns = [
    path("admin/", admin.site.urls),
    # Legacy /login/ bookmark → SPA sign-in
    path("login/", RedirectView.as_view(url="/signin/", permanent=False), name="login"),
    # django-two-factor registers this URL as two_factor:login; send users to the React app instead
    path(
        "account/login/",
        RedirectView.as_view(url="/signin/", permanent=False),
    ),
    # SPA shell + /api/* before two_factor so /signin/ and deep links are never shadowed
    path("", include("nomz.urls")),
    path("", include(tf_urls)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ✅ CRITICAL: React SPA catch-all (MUST BE LAST)
urlpatterns += [
    re_path(r"^.*$", spa_index, name="spa_index"),
]
