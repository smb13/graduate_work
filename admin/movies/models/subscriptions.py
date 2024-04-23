from http import HTTPStatus

import requests

from functools import cache

from django.contrib.auth import get_user
from django.db import models
from django.contrib import admin

import math
from unittest import mock

from django.core.paginator import Paginator
from django.contrib.admin.views.main import ChangeList

from config.components.auth import SERVICE_AUTH_API_BASE_PATH
from config.components.subscriptions import SUBSCRIPTIONS_SERVICE_HOST, SUBSCRIPTIONS_SERVICE_PORT, \
    SUBSCRIPTIONS_LIST_PER_PAGE


def get_elided_page_range(self, number=1, *, on_each_side=3, on_ends=2):

    if self.num_pages <= (on_each_side + on_ends) * 2:
        yield from range(1, self.num_pages + 1)
        return

    if number > (1 + on_each_side + on_ends) + 1:
        yield from range(1, on_ends + 1)
        yield Paginator.ELLIPSIS
        yield from range(number - on_each_side, number + 1)
    else:
        yield from range(1, number + 1)

    if number < (self.num_pages - on_each_side - on_ends) - 1:
        yield from range(number + 1, number + on_each_side + 1)
        yield Paginator.ELLIPSIS
        yield from range(self.num_pages - on_ends + 1, self.num_pages + 1)
    else:
        yield from range(number + 1, self.num_pages + 1)


class SubscriptionsChangeList(ChangeList):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_show_all = False
        self.multi_page = True
        self.result_count = 0
        self.list_editable = False

    def get_results(self, request):
        result = self.model_admin.get_list(request, self.page_num, self.list_per_page)
        items = result.get("items") or []
        total = result.get("total") or len(items)

        paginator = mock.MagicMock()
        paginator.count = total
        paginator.num_pages = int(math.ceil(total / self.list_per_page))
        paginator.get_elided_page_range = lambda *args, **kwargs: get_elided_page_range(paginator, *args, **kwargs)

        self.result_count = paginator.count
        self.full_result_count = paginator.count
        self.result_list = items
        self.paginator = paginator


class Subscription(models.Model):
    id = models.IntegerField("id", primary_key=True)
    name = models.CharField("Name", max_length=1024 * 3)
    description = models.TextField("Description")
    annual_price = models.IntegerField("Annual price")
    monthly_price = models.IntegerField("Monthly price")
    start_of_sales = models.DateTimeField("Start of sales")
    end_of_sales = models.DateTimeField("End of sales")

    @classmethod
    @cache
    def _fields_names(cls):
        return [f.name for f in Subscription._meta.fields]

    @classmethod
    def build_from(cls, data):
        return Subscription(**dict((field, data.get(field)) for field in cls._fields_names()))

    class Meta:
        managed = False
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"


class SubscriptionsAdmin(admin.ModelAdmin):
    list_per_page = SUBSCRIPTIONS_LIST_PER_PAGE
    list_display = ("id", "name", "description", "annual_price", "monthly_price", "start_of_sales", "end_of_sales")
    sortable_by = []
    fields = ["name", "description", "annual_price", "monthly_price", "start_of_sales"]

    def get_changelist(self, request: requests.Request, **kwargs):
        return SubscriptionsChangeList

    @staticmethod
    def access_token(request: requests.Request):
        return get_user(request).access_token

    @staticmethod
    def refresh_token(request: requests.Request):
        return get_user(request).refresh_token

    def get_readonly_fields(self, request, obj=None):
        return self.list_display

    def get_subscriptions_types(self, request: requests.Request) -> requests.Response:
        return requests.get(
            f'http://{SUBSCRIPTIONS_SERVICE_HOST}:{SUBSCRIPTIONS_SERVICE_PORT}/api/v1/subscription-types',
            headers={"Authorization": f"Bearer {self.access_token(request)}"}
        )

    def get_subscriptions_type(self, request: requests.Request, subscription_id) -> requests.Response:
        print(f'http://{SUBSCRIPTIONS_SERVICE_HOST}:{SUBSCRIPTIONS_SERVICE_PORT}'
            f'/api/v1/subscription-types/{subscription_id}')
        return requests.get(
            f'http://{SUBSCRIPTIONS_SERVICE_HOST}:{SUBSCRIPTIONS_SERVICE_PORT}'
            f'/api/v1/subscription-types/{subscription_id}',
            headers={"Authorization": f"Bearer {self.access_token(request)}"}
        )

    @staticmethod
    def refresh_access_token(request: requests.Request) -> None:
        user = get_user(request)
        response = requests.post(f"{SERVICE_AUTH_API_BASE_PATH}/auth/refresh?refresh_token={user.refresh_token}")
        user.access_token = response.json()["access_token"]
        user.refresh_token = response.json()["refresh_token"]
        user.save()

    def get_list(self, request, page_num, list_per_page):
        response = self.get_subscriptions_types(request)
        if response.status_code == HTTPStatus.FORBIDDEN:
            self.refresh_access_token(request)
            response = self.get_subscriptions_types(request)
            response.raise_for_status()
        elif response.status_code == HTTPStatus.OK:
            response.raise_for_status()

        items = [Subscription.build_from(item) for item in response.json()]
        items.sort(key=lambda item: item.id)
        return {
            "total": len(items),
            "items": items[(page_num-1)*list_per_page:page_num*list_per_page],
        }

    def get_object(self, request, object_id, *args, **kwargs):
        response = self.get_subscriptions_type(request, object_id)
        if response.status_code == HTTPStatus.FORBIDDEN:
            self.refresh_access_token(request)
            response = self.get_subscriptions_type(request, object_id)
            response.raise_for_status()
        elif response.status_code == HTTPStatus.OK:
            response.raise_for_status()
        elif response.status_code == HTTPStatus.NOT_FOUND:
            return Subscription()
        return Subscription(**response.json())


admin.site.register(Subscription, SubscriptionsAdmin)
