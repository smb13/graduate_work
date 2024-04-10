from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class FilmWorkTypeChoices(TextChoices):
    MOVIE = "movie", _("movie")
    TV_SHOW = "tv_show", _("tv_show")


class FilmWorkPersonRoleChoices(TextChoices):
    ACTOR = "actor", _("actor")
    DIRECTOR = "director", _("director")
    WRITER = "writer", _("writer")
