from config.components.base import env

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", default=False)

# Django-Silk
ENABLE_SILK = env("ENABLE_SILK", cast=bool, default=False)
# Django-Debug-Toolbar
ENABLE_DEBUG_TOOLBAR = env("ENABLE_DEBUG_TOOLBAR", cast=bool, default=False)

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django_extensions",
    "autocomplete_all",
    "corsheaders",
    "psqlextra",
    "rangefilter",
    "users.apps.UsersConfig",
    "movies.apps.MoviesConfig",
]

if ENABLE_SILK:
    INSTALLED_APPS = ["silk"] + INSTALLED_APPS
if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS = ["debug_toolbar"] + INSTALLED_APPS
