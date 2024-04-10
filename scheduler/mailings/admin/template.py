import uuid

from django import forms
from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from admin_extra_buttons.api import ExtraButtonsMixin, button
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from django_ace import AceWidget
from mailings.admin.task import MailingTaskAdminInline
from mailings.models import MailingTemplate
from mailings.tasks import task_send_mailings


class MailingTemplateForm(forms.ModelForm):
    source_code = forms.CharField(widget=AceWidget(mode="html", theme="chrome"))
    users_selector = forms.JSONField(widget=AceWidget(mode="json", theme="chrome"))

    class Meta:
        model = MailingTemplate
        fields = ("name", "source_code")


@admin.register(MailingTemplate)
class MailingTemplateAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    """Mailing template admin."""

    list_display = ("id", "name", "users_selector")
    inlines = (MailingTaskAdminInline,)
    form = MailingTemplateForm

    @button(
        label="Send mailing",
        html_attrs={"style": "background-color:#FFEA00;color:black"},
        name="send_mailing",
        change_form=True,
    )
    def send_mailing(self, request: HttpRequest, pk: uuid.UUID) -> HttpResponse:
        """Create mailing task manually"""
        template = self.get_object(request, pk)

        task_send_mailings.apply_async(
            args=(template.id,),
            kwargs=dict(name=template.name, users_selector=template.users_selector),
            expires=300,
        )

        self.message_user(request, "Mailing sent", messages.SUCCESS)

        return HttpResponseRedirectToReferrer(request)

    @button(
        label="Show Flower",
        html_attrs={"style": "background-color:#88FF88;color:black"},
        name="show_flower",
        change_form=True,
    )
    def show_flower(self, request: HttpRequest, pk: uuid.UUID) -> HttpResponse:
        """Redirect to celery flower"""
        return HttpResponseRedirect("/celery/")
