from config.components.base import env

SUBSCRIPTIONS_SERVICE_HOST = env("SUBSCRIPTION_SERVICE_HOST", cast=str, default="subscriptions")
SUBSCRIPTIONS_SERVICE_PORT = env("SUBSCRIPTION_SERVICE_PORT", cast=str, default="8000")

SUBSCRIPTIONS_LIST_PER_PAGE = 100
