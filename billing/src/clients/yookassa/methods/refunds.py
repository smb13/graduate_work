from aioyookassa.core.methods import APIMethod


class CreateRefund(APIMethod):
    """
    Create refund
    """

    http_method = "POST"
    path = "/refunds"

    @staticmethod
    def build_params(**kwargs) -> dict:
        return {
            "payment_id": kwargs.get("payment_id"),
            "amount": amount.dict() if (amount := kwargs.get("amount")) else None,
            "description": kwargs.get("description"),
            "receipt": receipt.dict() if (receipt := kwargs.get("receipt")) else None,
            "sources": [source.dict() for source in sources] if (sources := kwargs.get("sources")) else None,
            "deal": deal.dict() if (deal := kwargs.get("deal")) else None,
        }
