from django.core.exceptions import ValidationError

from crontab import CronTab
from jinja2 import Environment, TemplateSyntaxError


def validate_cron_expression(value: str) -> None:
    dummy_tab_item = CronTab(user=None).new("ls")
    try:
        dummy_tab_item.setall(value)
    except (ValueError, KeyError) as exc:
        raise ValidationError from exc


def validate_jinja2_syntax(value: str) -> None:
    try:
        env = Environment()
        env.parse(value)
    except TemplateSyntaxError as exc:
        raise ValidationError(message=exc.message) from exc
