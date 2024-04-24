from django.db import models
from django.utils.translation import gettext_lazy as _

from movies.models.common import TimeStampedMixin, UUIDMixin
from psqlextra.indexes import UniqueIndex


class Subscription(TimeStampedMixin):
    id = models.IntegerField("id", primary_key=True)
    name = models.CharField("Name", max_length=1024 * 3)
    description = models.TextField("Description")
    annual_price = models.IntegerField("Annual price")
    monthly_price = models.IntegerField("Monthly price")
    start_of_sales = models.DateTimeField("Start of sales")
    end_of_sales = models.DateTimeField("End of sales")

    class Meta:
        db_table = 'content"."subscription'
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")

    def __str__(self) -> str:
        return str(self.name)


class SubscriptionFilmWork(UUIDMixin):
    film_work = models.ForeignKey("FilmWork", on_delete=models.CASCADE)
    subscription = models.ForeignKey(
        "Subscription",
        on_delete=models.CASCADE,
        verbose_name=_("subscription"),
    )
    created = models.DateTimeField(auto_now_add=True)

    def get_results(self, request):
        exit(1)
        pass

    class Meta:
        db_table = 'content"."subscription_film_work'
        indexes = [
            UniqueIndex(
                fields=["film_work", "subscription"],
                name="film_work_subs_role_idx",
            ),
        ]
        verbose_name = _("subscription_film_work")
        verbose_name_plural = _("subscription_film_works")
