from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from home.feeds import LatestNewsFeed
from search import views as search_views
from sonum.views import clear_cache
from tweets import views as tweets_views

# Non-translatable URLs
# Note: if you are using the Wagtail API or sitemaps,
# these should not be added to `i18n_patterns` either
urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("tweets/", tweets_views.get_tweets, name="get_tweets"),
    path("backup/", include("telescoop_backup.urls")),
    path("cache/clear", clear_cache),
    path("latest/feed/", LatestNewsFeed()),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Translatable URLs
# These will be available under a language code prefix. For example /en/search/
urlpatterns += i18n_patterns(
    path("search/", search_views.search, name="search"),
    path("", include(wagtail_urls)),
)
