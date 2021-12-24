from .base import *  # noqa: F401,F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-d@_u0u0nqrqnl2g$eziedhsq#^=cgsuduug_ietvt3gi1wd-em"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS += ("debug_toolbar",)  # noqa: F405

MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)  # noqa: F405

BASE_URL = "http://localhost:8000/"


try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
