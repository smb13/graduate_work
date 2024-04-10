from django.http import HttpRequest, HttpResponse


def health_check_view(request: HttpRequest) -> HttpResponse:
    """Проверка работоспособности Django"""
    return HttpResponse(b'{"status": "ok"}', content_type="application/json")
