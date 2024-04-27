from http import HTTPStatus

from django.contrib.auth import get_user
from django.http import HttpRequest

import autocomplete_all as admin
import requests
from config.components.auth import SERVICE_AUTH_API_BASE_PATH
from config.components.subscriptions import SUBSCRIPTIONS_SERVICE_HOST, SUBSCRIPTIONS_SERVICE_PORT
from movies.models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork, Subscription, SubscriptionFilmWork
from rangefilter.filters import DateRangeFilter, NumericRangeFilter

from utils.paginator import RelTuplesPaginator


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ("name", "description")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ("full_name",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    readonly_fields = ("id",)
    list_display = ("id", "name", "description", "annual_price", "monthly_price", "start_of_sales", "end_of_sales")

    def has_add_permission(self, request: HttpRequest, obj: Subscription | None = None) -> bool:
        return False

    @staticmethod
    def access_token(request: HttpRequest) -> str:
        return get_user(request).access_token

    @staticmethod
    def refresh_token(request: HttpRequest) -> str:
        return get_user(request).refresh_token

    def get_readonly_fields(self, request: HttpRequest, obj: Subscription | None = None) -> tuple[str, ...]:
        return self.list_display

    def get_subscriptions_types(self, request: HttpRequest) -> requests.Response:
        return requests.get(
            f"http://{SUBSCRIPTIONS_SERVICE_HOST}:{SUBSCRIPTIONS_SERVICE_PORT}/api/v1/subscription-types",
            headers={"Authorization": f"Bearer {self.access_token(request)}"},
        )

    @staticmethod
    def refresh_access_token(request: HttpRequest) -> None:
        user = get_user(request)
        response = requests.post(f"{SERVICE_AUTH_API_BASE_PATH}/auth/refresh?refresh_token={user.refresh_token}")
        user.access_token = response.json()["access_token"]
        user.refresh_token = response.json()["refresh_token"]
        user.save()

    def get_search_results(
        self,
        request: HttpRequest,
        queryset: Subscription.queryset,
        search_term: str,
    ) -> tuple[Subscription.queryset, bool]:
        # Синхронизация с внешним сервисом подписок.
        response = self.get_subscriptions_types(request)

        if response.status_code == HTTPStatus.FORBIDDEN:
            self.refresh_access_token(request)
            response = self.get_subscriptions_types(request)
            response.raise_for_status()
        elif response.status_code == HTTPStatus.OK:
            response.raise_for_status()

        extsubs = {sub["id"]: Subscription(**sub) for sub in response.json()}

        for sub in Subscription.objects.all():
            if sub.id not in extsubs:
                sub.delete()
            else:
                extsubs[sub.id].created = sub.created
                extsubs[sub.id].save()
                extsubs.pop(sub.id)

        for sub in extsubs.values():
            sub.save()

        return super().get_search_results(request, queryset, search_term)


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork


class SubscriptionFilmWorkInline(admin.TabularInline):
    model = SubscriptionFilmWork


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    paginator = RelTuplesPaginator
    show_full_result_count = False

    inlines = (GenreFilmWorkInline, PersonFilmWorkInline, SubscriptionFilmWorkInline)

    list_display = ("title", "type", "creation_date", "rating")
    list_filter = (
        "type",
        ("creation_date", DateRangeFilter),
        ("rating", NumericRangeFilter),
        "genres",
    )
    search_fields = ("title", "description", "id")
