# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

from config.components.base import env

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_SCHEDULER_DB", default="scheduler_db"),
        "USER": env("POSTGRES_USER", default=""),
        "PASSWORD": env("POSTGRES_PASSWORD", default=""),
        "HOST": "postgres",
        "PORT": env("POSTGRES_PORT", default=5432),
        "OPTIONS": {
            # Нужно явно указать схемы, с которыми будет работать приложение.
            "options": "-c search_path=public,content",
        },
    },
}


CONN_MAX_AGE = 300  # https://docs.djangoproject.com/en/2.0/ref/databases/#persistent-connections
