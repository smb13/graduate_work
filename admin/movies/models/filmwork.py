from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from movies.choices import FilmWorkTypeChoices
from movies.models.common import TimeStampedMixin, UUIDMixin


class FilmWork(UUIDMixin, TimeStampedMixin):
    genres = models.ManyToManyField(
        "movies.Genre",
        through="movies.GenreFilmWork",
        verbose_name=_("genres"),
    )
    persons = models.ManyToManyField(
        "movies.Person",
        through="movies.PersonFilmWork",
        verbose_name=_("persons"),
    )

    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    creation_date = models.DateField(_("creation_date"), blank=True, null=True)
    rating = models.FloatField(
        _("rating"),
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )
    type = models.TextField(_("type"), choices=FilmWorkTypeChoices.choices)
    file_path = models.FileField(_("file"), blank=True, null=True, upload_to="movies/")

    class Meta:
        db_table = 'content"."film_work'
        indexes = [
            models.Index(
                fields=["creation_date", "rating"],
                name="creation_date_rating_idx",
            ),
        ]
        verbose_name = _("film_work")
        verbose_name_plural = _("film_works")

    def __str__(self) -> str:
        return str(self.title)
