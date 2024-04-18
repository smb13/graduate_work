from aioyookassa.core.client import YooKassa as BaseYooKassa
from aioyookassa.types.payment import Deal, PaymentAmount, Receipt
from clients.yookassa.methods.refunds import CreateRefund
from clients.yookassa.types import Refund, RefundSource


class YooKassa(BaseYooKassa):
    async def create_refund(
        self,
        payment_id: str,
        amount: PaymentAmount,
        description: str | None = None,
        receipt: Receipt | None = None,
        sources: list[RefundSource] | None = None,
        deal: Deal | None = None,
    ) -> Refund:
        """
        Create refund
        More detailed documentation:
        https://yookassa.ru/developers/api?codeLang=bash#create_refund

        :param deal: Deal data
        :param sources: Payment sources array (account ID and amount)
        :param receipt: Recept generation data
        :param description: Payment Description
        :param amount: Payment Amount
        :param payment_id: Payment ID to refund
        :return: Payment
        """

        params = CreateRefund.build_params(**locals())
        headers = {"Idempotence-Key": self._get_idempotence_key()}
        result = await self._send_request(CreateRefund, json=params, headers=headers)
        return Refund(**result)


yookassa: YooKassa | None = None


async def get_yookassa() -> YooKassa:
    if not yookassa:
        raise RuntimeError("YooKassa Client is not initialized")

    return yookassa
