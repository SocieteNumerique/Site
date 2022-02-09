from django.conf import settings
from django.utils import translation

from home.models import HomePage, NewsListPage
from home.templatetags.scheme_tags import scheme_page_url, news_page_url


class SearchDescriptionAndTranslationMiddleware:
    """Middleware to add search_description and seo_title to the context."""

    def __init__(self, get_response):
        from wagtail.core.models import Locale

        self.get_response = get_response
        locales = Locale.objects.all()
        language_to_locale_id = {locale.language_code: locale.id for locale in locales}
        self.home_pages = {
            locale.language_code: HomePage.objects.get(
                locale=language_to_locale_id[locale.language_code]
            )
            for locale in locales
        }
        self.news_list_pages = {
            locale.language_code: NewsListPage.objects.get(
                locale=language_to_locale_id[locale.language_code]
            )
            for locale in locales
        }

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        context = response.context_data
        seo_title = None
        description = "Le Programme Société Numérique de l’Agence Nationale de la Cohésion des Territoires œuvre en faveur d’un numérique d’intérêt général en offrant à tous et toutes les clés d’appropriation du numérique."
        current_language = translation.get_language()
        translated_language = [
            language[0]
            for language in settings.LANGUAGES
            if language[0] != current_language
        ][0]
        translated_home_page = self.home_pages[translated_language]
        translated_url = translated_home_page.url

        if not context:
            return response
        if context.get("scheme"):
            try:
                translated_scheme = context.get("scheme").get_translations()[0]
            except IndexError:
                translated_scheme = context.get("scheme")
            translated_url = scheme_page_url(translated_home_page, translated_scheme)
            seo_title = context.get("scheme").name
            if context.get("scheme").search_description:
                description = context.get("scheme").search_description
        elif context.get("news"):
            try:
                translated_news = context.get("news").get_translations()[0]
            except IndexError:
                translated_news = context.get("news")
            translated_news_list_page = self.news_list_pages[translated_language]
            translated_url = news_page_url(translated_news_list_page, translated_news)
            seo_title = context.get("news").name
            if context.get("news").search_description:
                description = context.get("news").search_description
        elif context.get("page"):
            page_translation = context.get("page").get_translations()[0]
            if page_translation:
                translated_url = page_translation.url
            if context.get("page").search_description:
                # for pages, seo_title and title are already correctly taken in to account
                description = context.get("page").search_description

        context["search_description"] = description
        context["seo_title"] = seo_title
        context["translated_url"] = translated_url
        return response
