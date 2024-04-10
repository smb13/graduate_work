"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from utils.views import flower_proxy, health_check_view

urlpatterns_api = [
    path("api/v1/", include("mailings.api.v1.urls", namespace="mailings-api-v1")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthcheck/", health_check_view),
    *urlpatterns_api,
    path(
        "api/scheme/",
        SpectacularAPIView.as_view(
            urlconf=urlpatterns_api,
            custom_settings={
                "TITLE": "Scheduler API",
                "VERSION": "v1",
            },
        ),
        name="schema",
    ),
    path("api/openapi/", SpectacularSwaggerView.as_view(url_name="schema"), name="schema-openapi"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="schema-redoc"),
    # Проксируем доступ к статистике celery (flower) через django
    re_path(rf"^{settings.FLOWER_URL_PREFIX}/(?P<path>.*)", flower_proxy, name="celery"),
]
