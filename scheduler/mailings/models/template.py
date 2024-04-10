import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from mailings.methods import validate_jinja2_syntax


class MailingTemplate(models.Model):
    """Mailing template model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name=_("name"))
    source_code = models.TextField(blank=True, verbose_name=_("html source code"), validators=[validate_jinja2_syntax])
    users_selector = models.JSONField(blank=True, verbose_name=_("users selector"), default=dict)

    class Meta:
        db_table = 'content"."mailing_template'
        verbose_name_plural = _("Mailing templates")
        verbose_name = _("Mailing template")

    def __str__(self) -> str:
        return f"{self.id} {self.name}"

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
