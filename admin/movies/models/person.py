from django.db import models
from django.utils.translation import gettext_lazy as _

from movies.choices import FilmWorkPersonRoleChoices
from movies.models.common import TimeStampedMixin, UUIDMixin
from psqlextra.indexes import UniqueIndex


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(_("full_name"))

    class Meta:
        db_table = 'content"."person'
        verbose_name = _("person")
        verbose_name_plural = _("persons")

    def __str__(self) -> str:
        return str(self.full_name)


class PersonFilmWork(UUIDMixin):
    film_work = models.ForeignKey("FilmWork", on_delete=models.CASCADE)
    person = models.ForeignKey(
        "Person",
        on_delete=models.CASCADE,
        verbose_name=_("person"),
    )
    role = models.TextField(
        _("role"),
        choices=FilmWorkPersonRoleChoices.choices,
        blank=True,
    )  # Невозможно использовать Choices т.к. нет ТЗ на значения
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        indexes = [
            UniqueIndex(
                fields=["film_work", "person", "role"],
                name="film_work_person_role_idx",
            ),
        ]
        verbose_name = _("person_film_work")
        verbose_name_plural = _("person_film_works")
