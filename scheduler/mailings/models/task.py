import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

import timezone_field
from cron_descriptor import FormatException, MissingFieldException, WrongArgumentException, get_description
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from mailings.methods import validate_cron_expression
from mailings.models.template import MailingTemplate


class MailingTask(models.Model):
    """Mailing task model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=255, blank=True, default="", verbose_name=_("description"))
    template = models.ForeignKey(MailingTemplate, on_delete=models.PROTECT, verbose_name=_("template"))
    timezone = timezone_field.TimeZoneField(
        default="UTC",
        use_pytz=False,
        verbose_name=_("cron timezone"),
        help_text="Timezone to Run the Cron Schedule on. Default is UTC.",
    )
    periodic_task = models.OneToOneField(
        PeriodicTask,
        on_delete=models.PROTECT,
        verbose_name=_("periodic task"),
        editable=False,
    )
    crontab_schedule = models.OneToOneField(
        CrontabSchedule,
        on_delete=models.PROTECT,
        verbose_name=_("periodic task"),
        editable=False,
    )
    cron_expression = models.CharField(
        verbose_name=_("schedule"),
        max_length=32,
        validators=[validate_cron_expression],
        help_text='cron expression "MINUTE HOUR DAY MONTH DAY OF WEEK", '
        'for example: "* * * * *" (every minute), '
        '"30 6 * * *" (every day at 6:30), '
        '"0 12 * * 1-5" (at 12:00 on Monday through Friday); '
        "more details here: https://en.wikipedia.org/wiki/Cron",
    )

    class Meta:
        db_table = 'content"."mailing_task'
        verbose_name_plural = _("Mailing tasks")
        verbose_name = _("Mailing task")

    def __str__(self) -> str:
        return f"{self.id} {self.description} ({self.human_readable})"

    def clean(self) -> None:
        schedule = dict(
            zip(
                ["minute", "hour", "day_of_month", "month_of_year", "day_of_week"],
                self.cron_expression.split(" "),
            ),
        )

        if not hasattr(self, "crontab_schedule") or not self.crontab_schedule:
            self.crontab_schedule = CrontabSchedule.objects.create(timezone=self.timezone, **schedule)
        else:
            for key, value in schedule.items():
                setattr(self.crontab_schedule, key, value)
            self.crontab_schedule.timezone = self.timezone
            self.crontab_schedule.save()

        if not hasattr(self, "periodic_task") or not self.periodic_task:
            self.periodic_task = PeriodicTask.objects.create(
                name=self.description,
                task="task_send_mailings",
                crontab=self.crontab_schedule,
            )
        else:
            self.periodic_task.name = self.description
            self.periodic_task.task = "task_send_mailings"
            self.periodic_task.save()

        super().clean()

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def human_readable(self) -> str:
        try:
            human_readable = get_description(self.cron_expression)
        except (
            MissingFieldException,
            FormatException,
            WrongArgumentException,
        ):
            return f"{self.cron_expression} {str(self.timezone)}"
        return f"{human_readable} {str(self.timezone)}"
