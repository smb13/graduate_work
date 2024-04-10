import autocomplete_all as admin
from movies.models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork
from rangefilter.filters import DateRangeFilter, NumericRangeFilter

from utils.paginator import RelTuplesPaginator


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ("name", "description")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ("full_name",)


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    paginator = RelTuplesPaginator
    show_full_result_count = False

    inlines = (GenreFilmWorkInline, PersonFilmWorkInline)

    list_display = ("title", "type", "creation_date", "rating")
    list_filter = (
        "type",
        ("creation_date", DateRangeFilter),
        ("rating", NumericRangeFilter),
        "genres",
    )
    search_fields = ("title", "description", "id")
