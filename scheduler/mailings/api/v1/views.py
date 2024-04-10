from rest_framework.viewsets import ReadOnlyModelViewSet

from mailings.api.v1.serializers import MailingTemplateSerializer
from mailings.models import MailingTemplate


class MailingTemplateViewSet(ReadOnlyModelViewSet):
    serializer_class = MailingTemplateSerializer
    queryset = MailingTemplate.objects.all()
