from config.components.base import env

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = env("STATIC_URL", default="static/")
STATIC_ROOT = env("STATIC_ROOT", default="data/static/")

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

STATICFILES_DIRS = ("static/",)

MEDIA_URL = env("MEDIA_URL", default="media/")
MEDIA_ROOT = env("MEDIA_ROOT", default="data/media/")

DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 10 MB
