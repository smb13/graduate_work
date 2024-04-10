from rest_framework import serializers

from mailings.models import MailingTemplate


class MailingTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailingTemplate
        fields = ("id", "name", "source_code")
