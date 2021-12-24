from collections import defaultdict
from typing import Dict, Union
import datetime

from django.conf import settings
from django.utils import translation

STANDARD_PAGES_CONF = {
    "news": "actualite",
    "mission": "mission",
    "accessibility": "accessibilite",
    "legal_notices": "mentions-legales",
    "root": "accueil",
}
DEFAULT_LANGUAGE = settings.LANGUAGES[0][0]
LAST_UPDATE: Dict[str, Union[None, datetime.datetime]] = {
    "standard_pages": None,
    "menu_pages": None,
    "schemes": None,
}


def is_recent(key: str):
    """Check if values for the given key have been updated recently."""
    if not LAST_UPDATE[key]:
        return False
    return (datetime.datetime.now() - LAST_UPDATE[key]).total_seconds() < 60  # type: ignore


def update_last_change(key):
    """Mark key as last updated now."""
    LAST_UPDATE[key] = datetime.datetime.now()


def load_standard_pages():
    """
    Returns context with standard pages for each language, such as
    {
        "fr": {
            "legal_notices_page": <Page: Mentions légales>,
            "accessibility_page": <Page: Accessibilité>,
            ...
        },
        "en": {
            "legal_notices_page": <Page: Legal Notices>,
            "accessibility_page": <Page: Accesibility>,
            ...
        }

    }
    """
    # This cannot be done in the main body of the page, because models
    # are not yet loaded when this page is imported in the settings.
    from wagtail.core.models import Page, Locale
    from home.models import News

    language_to_locale_id = {
        locale.language_code: locale.id for locale in Locale.objects.all()
    }
    standard_pages_per_language = defaultdict(dict)
    default_locale_id = language_to_locale_id[DEFAULT_LANGUAGE]

    def get_localized_page(page: Page, language: str) -> Page:
        if language == settings.LANGUAGES[0][0]:
            return page
        locale_id = language_to_locale_id[language]
        return Page.objects.filter(
            translation_key=page.translation_key, locale_id=locale_id
        ).first()

    for page_name, page_slug in STANDARD_PAGES_CONF.items():
        for language_code, locale_id in language_to_locale_id.items():
            if (
                page_name == "news"
                and News.objects.filter(locale_id=locale_id).count() == 0
            ):
                continue
            page_in_default_language = Page.objects.filter(
                slug=page_slug, locale_id=default_locale_id
            ).first()
            if page_in_default_language:
                localized_page = get_localized_page(
                    page_in_default_language, language_code
                )
            else:
                localized_page = None
            standard_pages_per_language[language_code][
                f"{page_name}_page"
            ] = localized_page

    return dict(standard_pages_per_language)


def load_additional_menu_pages():
    """
    Returns context with pages_in_menu for each language, such as
    {
        "fr": <QuerySet: Page>,
        "en": <QuerySet: Page>
    }
    """
    # This cannot be done in the main body of the page, because models
    # are not yet loaded when this page is imported in the settings.
    from wagtail.core.models import Page, Locale

    language_to_locale_id = {
        locale.language_code: locale.id for locale in Locale.objects.all()
    }
    menu_pages_per_language = defaultdict(dict)

    for language_code, locale_id in language_to_locale_id.items():
        translation_keys_of_pages_in_menu = (
            Page.objects.filter(locale_id=locale_id)
            .exclude(slug="mission")
            .live()
            .in_menu()
        ).values_list("translation_key", flat=True)
        pages_in_menu = (
            Page.objects.filter(locale_id=locale_id)
            .filter(translation_key__in=translation_keys_of_pages_in_menu)
            .live()
            .in_menu()
            .exclude(slug="mission")
        )

        menu_pages_per_language[language_code]["pages_in_menu"] = pages_in_menu

    return dict(menu_pages_per_language)


def load_schemes_list():
    """
    Returns context with schemes list for each language, such as
    {
        "fr": <QuerySet: Scheme>,
        "en": <QuerySet: Scheme>
    }
    """
    # This cannot be done in the main body of the page, because models
    # are not yet loaded when this page is imported in the settings.
    from wagtail.core.models import Locale
    from home.models import Scheme

    language_to_locale_id = {
        locale.language_code: locale.id for locale in Locale.objects.all()
    }
    schemes_per_language = defaultdict(dict)
    for language_code, locale_id in language_to_locale_id.items():
        schemes_per_language[language_code]["schemes"] = Scheme.objects.filter(
            locale_id=locale_id
        )
    return dict(schemes_per_language)


def standard_pages(_):
    """
    Returns context with standard pages for current_language, such as
    {
        "legal_notices_page": <Page: Legal Notices>,
        "accessibility_page": <Page: Accesibility>,
        ...
    }
    """
    if not is_recent("standard_pages"):
        update_last_change("standard_pages")
        standard_pages._standard_pages = load_standard_pages()
    return standard_pages._standard_pages[translation.get_language()]


def additional_menu_pages(_):
    """
    Returns context with additional menu pages for current_language
    {
        "pages_in_menu": <QuerySet: Page>,
    }
    """
    if not is_recent("menu_pages"):
        update_last_change("menu_pages")
        additional_menu_pages._menu_pages = load_additional_menu_pages()
    return additional_menu_pages._menu_pages[translation.get_language()]


def language(_):
    """Templates need a language_code. Will be overriden by django if defined."""
    return {"language_code": translation.get_language()}


def schemes_list(_):
    """
    Returns context with schemes for current_language
    {
        "schemes": <QuerySet: Scheme>,
    }
    """
    if not is_recent("schemes"):
        update_last_change("schemes")
        schemes_list._schemes_list = load_schemes_list()
    return schemes_list._schemes_list[translation.get_language()]
