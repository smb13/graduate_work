from rest_framework.routers import DefaultRouter

from mailings.api.v1.views import MailingTemplateViewSet

app_name = "mailings-api-v1"

router = DefaultRouter()
router.register(r"templates", MailingTemplateViewSet, basename="templates")

urlpatterns = router.urls
