from django.db import models
from django.utils.translation import gettext_lazy as _

from movies.models.common import TimeStampedMixin, UUIDMixin
from psqlextra.indexes import UniqueIndex


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = _("genre")
        verbose_name_plural = _("genres")

    def __str__(self) -> str:
        return str(self.name)


class GenreFilmWork(UUIDMixin):
    film_work = models.ForeignKey("FilmWork", on_delete=models.CASCADE)
    genre = models.ForeignKey(
        "Genre",
        on_delete=models.CASCADE,
        verbose_name=_("genre"),
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        indexes = [
            UniqueIndex(fields=["film_work", "genre"], name="film_work_genre_idx"),
        ]
        verbose_name = _("genre_film_work")
        verbose_name_plural = _("genre_film_works")
