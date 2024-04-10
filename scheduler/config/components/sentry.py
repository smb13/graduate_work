import sentry_sdk
from config.components.base import env
from sentry_sdk.integrations.django import DjangoIntegration

# Инициализация Sentry SDK если есть env SENTRY_DSN
if SENTRY_DSN := env("SENTRY_DSN", default=""):
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        enable_tracing=True,
        integrations=[DjangoIntegration()],
        traces_sample_rate=env("TRACES_SAMPLE_RATE", cast=float, default=0.1),
        profiles_sample_rate=env("PROFILES_SAMPLE_RATE", cast=float, default=0.1),
        attach_stacktrace=True,
        send_default_pii=True,
    )
