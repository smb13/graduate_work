from django import forms
from django.contrib import admin
from django.forms import ChoiceField

from mailings.models import MailingTask
from timezone_field.backends import get_tz_backend
from timezone_field.choices import with_gmt_offset


class MailingTaskForm(forms.ModelForm):
    timezone = ChoiceField(
        choices=sorted(with_gmt_offset(get_tz_backend(False).base_tzstrs, use_pytz=False), key=lambda x: x[1].lower()),
    )

    class Meta:
        model = MailingTask
        fields = ("description", "timezone", "cron_expression", "template")


@admin.register(MailingTask)
class MailingTaskAdmin(admin.ModelAdmin):
    """Mailing task admin."""

    form = MailingTaskForm

    list_display = ("id", "human_readable", "template", "timezone", "crontab_schedule")
    list_filter = ("template", "timezone")


class MailingTaskInlineForm(forms.ModelForm):
    timezone = ChoiceField(
        choices=sorted(with_gmt_offset(get_tz_backend(False).base_tzstrs, use_pytz=False), key=lambda x: x[1].lower()),
    )

    class Meta:
        model = MailingTask
        fields = ("description", "timezone", "cron_expression")


class MailingTaskAdminInline(admin.TabularInline):
    model = MailingTask
    extra = 0
    form = MailingTaskInlineForm
