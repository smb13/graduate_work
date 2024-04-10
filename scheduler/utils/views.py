from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import proxy.views


def health_check_view(request: HttpRequest) -> HttpResponse:
    """Проверка работоспособности Django"""
    return HttpResponse(b'{"status": "ok"}', content_type="application/json")


@csrf_exempt
@user_passes_test(lambda user: user.is_superuser)
def flower_proxy(request: HttpRequest, path: str) -> HttpResponse:
    url = f"{settings.FLOWER_HOST}:{settings.FLOWER_PORT}/{settings.FLOWER_URL_PREFIX}/"
    return proxy.views.proxy_view(request, url + path)
