from .base import *  # noqa: F401,F403

import rollbar

DEBUG = False

SECRET_KEY = config.getstr("security.secret_key")  # noqa: F405
ALLOWED_HOSTS = config.getlist("security.allowed_hosts")  # noqa: F405
STATIC_ROOT = config.getstr("staticfiles.static_root")  # noqa: F405

# cache and minify
MIDDLEWARE = (
    [
        "django.middleware.cache.UpdateCacheMiddleware",
        "htmlmin.middleware.HtmlMinifyMiddleware",
    ]
    + MIDDLEWARE  # noqa: F405
    + [
        "django.middleware.cache.FetchFromCacheMiddleware",
        "htmlmin.middleware.MarkRequestMiddleware",
    ]
)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": "127.0.0.1:11211",
    }
}
CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_SECONDS = 30
CACHE_MIDDLEWARE_KEY_PREFIX = ""

# rollbar
MIDDLEWARE.append(  # noqa: F405
    "rollbar.contrib.django.middleware.RollbarNotifierMiddleware"
)
ROLLBAR = {
    "access_token": "1650e242bbc04ef68e7f93923fcaa157",
    "environment": "production",
    "root": BASE_DIR,  # noqa: F405
}
rollbar.init(**ROLLBAR)
