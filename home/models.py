import datetime
import json
from typing import List

from django import forms
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalManyToManyField
from taggit.models import TagBase
from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
    MultiFieldPanel,
)
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.core import blocks
from wagtail.core.blocks import ListBlock
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, TranslatableMixin
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.models import Image
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail_localize.segments.extract import StreamFieldSegmentExtractor
from wagtail_localize.segments.ingest import StreamFieldSegmentsWriter

from home.constants import NEWS_SLUG

# in wagtail-localize==1.0, StreamFieldSegmentExtractor is not able to
# handle list blocks, so we monkey patch it.
def custom_handle_list_block(self, list_block):
    print("### handle_list_block", list_block)
    segments = []
    for block in list_block:
        segments.extend(self.handle_block(block.block, block))
    print("### segments", segments)
    return segments


StreamFieldSegmentExtractor.handle_list_block = custom_handle_list_block


def ingestor_handle_list_block(self, list_block, segments):
    for block_index, block in enumerate(list_block):
        sub_segments = segments[2 * block_index : 2 * (block_index + 1)]
        self.handle_block(block.block, block, sub_segments)
    return list_block


StreamFieldSegmentsWriter.handle_list_block = ingestor_handle_list_block


class FreeBodyField(models.Model):
    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="full title", label="titre")),
            (
                "paragraph",
                blocks.StructBlock(
                    [
                        (
                            "image",
                            ImageChooserBlock(
                                label="Petite image à gauche du texte", required=False
                            ),
                        ),
                        (
                            "paragraph",
                            blocks.RichTextBlock(
                                label="paragraphe",
                                features=[
                                    "h3",
                                    "h4",
                                    "bold",
                                    "italic",
                                    "link",
                                    "ol",
                                    "ul",
                                    "embed",
                                    "hr",
                                ],
                            ),
                        ),
                    ],
                    label="paragraphe",
                ),
            ),
            ("image", ImageChooserBlock()),
            (
                "key_figure",
                blocks.ListBlock(
                    blocks.StructBlock(
                        [
                            ("figure", blocks.CharBlock(label="chiffre")),
                            ("label", blocks.CharBlock(label="label")),
                        ]
                    ),
                    label="chiffre clé",
                ),
            ),
            (
                "quote",
                blocks.StructBlock(
                    [
                        (
                            "source_link",
                            blocks.CharBlock(
                                label="lien vers la source", required=False
                            ),
                        ),
                        ("quote", blocks.CharBlock(label="citation")),
                        ("author", blocks.CharBlock(label="auteurice", required=False)),
                        ("book", blocks.CharBlock(label="livre", required=False)),
                        ("details", blocks.CharBlock(label="détails", required=False)),
                        ("image", ImageChooserBlock(required=False)),
                    ],
                    label="citation",
                ),
            ),
            ("pdf", DocumentChooserBlock()),
            (
                "call_out",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(label="Titre")),
                        ("text", blocks.CharBlock(label="Texte")),
                        (
                            "button",
                            blocks.CharBlock(label="Texte du bouton", required=False),
                        ),
                        (
                            "button_target",
                            blocks.BooleanBlock(
                                default=False,
                                label="Ouvre un nouvel onglet ?",
                                required=False,
                            ),
                        ),
                        (
                            "button_link",
                            blocks.CharBlock(label="Lien du bouton", required=False),
                        ),
                    ],
                    label="Mise en avant",
                ),
            ),
            ("highlight", blocks.CharBlock(label="mise en exergue")),
            (
                "iframe",
                blocks.StructBlock(
                    [
                        ("url", blocks.CharBlock(label="Url")),
                        ("legend", blocks.CharBlock(label="Légende")),
                        (
                            "height",
                            blocks.IntegerBlock(
                                label="Hauteur en pourcentage d'écran",
                                default=50,
                                min_value=0,
                                max_value=100,
                            ),
                        ),
                    ],
                    label="Cadre intégré (iframe)",
                ),
            ),
            (
                "call_to_action",
                blocks.StructBlock(
                    [
                        ("text", blocks.CharBlock(label="Texte", max_length=72)),
                        (
                            "url",
                            blocks.URLBlock(label="Lien externe", required=False),
                        ),
                        (
                            "centered",
                            blocks.BooleanBlock(
                                default=False,
                                label="Centrer le bouton ? (Si non alignement à gauche)",
                                required=False,
                            ),
                        ),
                    ],
                    label="Bouton",
                ),
            ),
        ],
        blank=True,
        verbose_name="description",
        help_text="Corps de la page",
    )

    panels = [
        StreamFieldPanel("body", classname="full"),
    ]

    class Meta:
        abstract = True


class HomePage(RoutablePageMixin, Page):
    # HomePage can be created only on the root
    parent_page_types = ["wagtailcore.Page"]

    mission_call_action = models.CharField(
        verbose_name="résumé de notre mission", max_length=255
    )
    news_block_title = models.CharField(
        blank=True,
        verbose_name="titre du block d'actualité",
        max_length=255,
        help_text="Si ce champ est vide la mise en avant des actualités ne s'affichera pas sur l'accueil",
    )
    news_first = models.ForeignKey(
        "home.News",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Première actualité",
        help_text="Première actualité à mettre en avant sur la page d'accueil",
    )
    news_second = models.ForeignKey(
        "home.News",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Second actualité",
        help_text="Deuxième actualité à mettre en avant sur la page d'accueil",
    )

    content_panels = Page.content_panels + [
        FieldPanel("mission_call_action"),
        MultiFieldPanel(
            [
                FieldPanel("news_block_title"),
                SnippetChooserPanel("news_first"),
                SnippetChooserPanel("news_second"),
            ],
            heading="Mise en avant d'actualités",
        ),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["tags"] = {
            "who": ForWhoTag.objects.all(),
            "what": ForWhatTag.objects.all(),
        }
        context["selected_tags"] = {
            "who": ForWhoTag.objects.filter(name__in=request.GET.getlist("who")),
            "what": ForWhatTag.objects.filter(name__in=request.GET.getlist("what")),
        }
        self.get_news_promoted(context)
        context["news_list_page"] = NewsListPage.objects.filter(
            locale_id=self.locale_id
        ).get()

        # context for JS tag-based scheme filtering
        schemes_with_tag = {
            "who": {},
            "what": {},
        }
        who_tags = ForWhoTag.objects.filter(locale_id=self.locale_id)
        what_tags = ForWhatTag.objects.filter(locale_id=self.locale_id)
        for tag in who_tags:
            schemes_with_tag["who"][tag.pk] = list(
                tag.scheme_set.filter(locale_id=self.locale_id).values_list(
                    "pk", flat=True
                )
            )
        for tag in what_tags:
            schemes_with_tag["what"][tag.pk] = list(
                tag.scheme_set.filter(locale_id=self.locale_id).values_list(
                    "pk", flat=True
                )
            )

        context["schemes_with_tag"] = json.dumps(schemes_with_tag)
        context["scheme_ids"] = json.dumps(
            list(
                Scheme.objects.filter(locale_id=self.locale_id).values_list(
                    "pk", flat=True
                )
            )
        )
        context["tag_ids"] = json.dumps(
            {
                "who": list(who_tags.values_list("pk", flat=True)),
                "what": list(what_tags.values_list("pk", flat=True)),
            }
        )
        try:
            context["default_news_image"] = Image.objects.get(title="journal")
        except Image.DoesNotExist:
            context["default_news_image"] = None
        return context

    def get_news_promoted(self, context):
        context["news_promoted"] = []
        context["news_promoted_linked_schemes"] = set()
        if self.news_first and self.news_first.locale_id == self.locale_id:
            context["news_promoted"].append(self.news_first)
            context["news_promoted_linked_schemes"].update(
                scheme.name for scheme in self.news_first.schemes.all()
            )
        if self.news_second and self.news_first.locale_id == self.locale_id:
            context["news_promoted"].append(self.news_second)
            context["news_promoted_linked_schemes"].update(
                scheme.name for scheme in self.news_second.schemes.all()
            )

    @route(r"^dispositif/(.*)/$", name="scheme")
    def access_scheme_page(self, request, slug):
        scheme = Scheme.objects.get(slug=slug)
        return self.render(
            request,
            context_overrides={
                "scheme": scheme,
                "home_page": HomePage.objects.filter(locale_id=self.locale_id).get(),
            },
            template="home/scheme_page.html",
        )

    def __init__(self, *args, **kwargs):
        """Fixes a bug when trying to translate."""
        if "index_entries" in kwargs:
            kwargs.pop("index_entries")
        super().__init__(*args, **kwargs)


class NewsListPage(RoutablePageMixin, Page):
    class Meta:
        verbose_name = "Accueil des actualités"
        verbose_name_plural = "Accueils des actualités"

    parent_page_types = ["home.HomePage"]
    subpage_types: List[str] = []
    max_count_per_parent = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        all_news_list = self.get_news_filtered(request)
        paginator = Paginator(all_news_list, 12)
        page = request.GET.get("page")
        try:
            news_list = paginator.page(page)
        except PageNotAnInteger:
            news_list = paginator.page(1)
        except EmptyPage:
            # If the ?page=x is out of range (too high most likely)
            news_list = paginator.page(paginator.num_pages)
        context["news_list"] = news_list
        context["news_type"] = ["Evènement", "Actualité"]
        context["selected_news_type"] = request.GET.getlist("filtre")
        return context

    def get_news_filtered(self, request):
        events_checked = "Evènement" in request.GET.getlist("filtre")
        news_checked = "Actualité" in request.GET.getlist("filtre")
        if news_checked and not events_checked:
            return News.objects.filter(locale_id=self.locale_id, is_event=False)
        if not news_checked and events_checked:
            return News.objects.filter(locale_id=self.locale_id, is_event=True)
        return News.objects.filter(locale_id=self.locale_id)

    @route(r"^(.*)/$", name="news")
    def access_news_page(self, request, news_slug):
        news = News.objects.get(slug=news_slug)
        return self.render(
            request,
            context_overrides={
                "news": news,
                "home_page": HomePage.objects.filter(locale_id=self.locale_id).get(),
                "news_page": NewsListPage.objects.filter(
                    locale_id=self.locale_id
                ).get(),
                "other_news_list": News.objects.filter(
                    locale_id=self.locale_id
                ).exclude(id=news.id)[:3],
            },
            template="home/news_page.html",
        )

    def save(self, *args, **kwargs):
        self.slug = NEWS_SLUG
        super().save(*args, **kwargs)


class ContentPage(Page, FreeBodyField):
    class Meta:
        verbose_name = "Page de contenu"
        verbose_name_plural = "Pages de contenu"

    subpage_types: List[str] = []

    schemes = ParentalManyToManyField(
        "home.Scheme", blank=True, verbose_name="Dispositifs liés"
    )

    content_panels = (
        Page.content_panels
        + FreeBodyField.panels
        + [
            FieldPanel("schemes", widget=forms.CheckboxSelectMultiple),
        ]
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        return context

    def get_template(self, request, *args, **kwargs):
        template = super().get_template(request, *args, **kwargs)
        if "/mission/" in request.path:
            template = "home/mission_page.html"
        return template


class TranslatedTagMixin(TranslatableMixin):
    class Meta:
        abstract = True

    long_name = models.CharField(
        verbose_name="nom du filtre",
        max_length=255,
        help_text="Nom du filtre tel que l'utilisateur le voit affiché (peut être plus précis que le nom du tag)",
    )
    name_en = models.CharField(verbose_name="nom anglais", max_length=100)
    long_name_en = models.CharField(
        verbose_name="nom anglais du filtre",
        max_length=255,
        help_text="Nom du filtre tel que l'utilisateur le voit affiché (peut être plus précis que le nom du tag)",
    )

    @property
    def localized_name(self):
        default_language = "fr"
        language = translation.get_language()
        if language == default_language:
            return self.name
        return getattr(self, f"name_{language}")

    @property
    def localized_long_name(self):
        default_language = "fr"
        language = translation.get_language()
        if language == default_language:
            return self.long_name
        return getattr(self, f"long_name_{language}")


class ForWhatTag(TagBase, TranslatedTagMixin):
    class Meta(TranslatableMixin.Meta):
        verbose_name = "tag 'Pour quoi?'"
        verbose_name_plural = "tags 'Pour quoi?'"


class ForWhoTag(TagBase, TranslatedTagMixin):
    class Meta(TranslatableMixin.Meta):
        verbose_name = "tag 'Pour qui?'"
        verbose_name_plural = "tags 'Pour qui?'"


class SeoFieldsMixin(models.Model):
    class Meta:
        abstract = True

    seo_title = models.CharField(
        verbose_name=_("title tag"),
        max_length=255,
        blank=True,
        help_text=_(
            "The name of the page displayed on search engine results as the clickable headline."
        ),
    )
    search_description = models.TextField(
        verbose_name=_("meta description"),
        blank=True,
        help_text=_(
            "The descriptive text displayed underneath a headline in search engine results."
        ),
    )


@register_snippet
class Scheme(index.Indexed, TranslatableMixin, FreeBodyField, SeoFieldsMixin):
    name = models.CharField(verbose_name="nom", max_length=255)
    short_description = models.CharField(
        verbose_name="description courte", max_length=510
    )
    slug = models.SlugField(max_length=100, verbose_name="slug (URL de l'actualité)")
    external_link = models.CharField(
        verbose_name="lien externe",
        blank=True,
        null=True,
        max_length=300,
        help_text="ignorer la description s'il y a un lien externe",
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    youtube_video_id = models.CharField(max_length=15, null=True, blank=True)

    for_what_tags = models.ManyToManyField(
        ForWhatTag, blank=True, verbose_name="Tags 'Pour quoi?'"
    )
    for_who_tags = models.ManyToManyField(
        ForWhoTag, blank=True, verbose_name="Tags 'Pour qui?'"
    )
    schemes = models.ManyToManyField(
        "home.Scheme", blank=True, verbose_name="Dispositifs reliés"
    )

    search_fields = [
        index.SearchField("name", partial_match=True),
    ]

    panels = [
        FieldPanel("name"),
        FieldPanel("short_description", classname="full"),
        FieldPanel("slug", classname="full"),
        FieldPanel("for_what_tags", widget=forms.CheckboxSelectMultiple),
        FieldPanel("for_who_tags", widget=forms.CheckboxSelectMultiple),
        FieldPanel("external_link", classname="collapsible"),
        ImageChooserPanel("image", classname="collapsible"),
        FieldPanel("youtube_video_id", classname="collapsible"),
        FieldPanel("schemes", widget=forms.CheckboxSelectMultiple),
    ] + FreeBodyField.panels

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        """Fixes a bug when trying to translate."""
        if "index_entries" in kwargs:
            kwargs.pop("index_entries")
        super().__init__(*args, **kwargs)

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Dispositifs"
        verbose_name = "Dispositif"


@register_snippet
class News(index.Indexed, TranslatableMixin, FreeBodyField, SeoFieldsMixin):
    name = models.CharField(verbose_name="nom", max_length=255)
    short_description = models.CharField(
        verbose_name="description courte", max_length=510, blank=True, null=True
    )
    slug = models.SlugField(max_length=100, verbose_name="slug (URL de l'actualité)")
    publication_date = models.DateTimeField(
        verbose_name="Date de publication",
        default=datetime.datetime.now,
        help_text="Permet de trier l'ordre d'affichage dans /actualites",
    )
    is_event = models.BooleanField(default=False, verbose_name="Est un évènement ?")
    start_date = models.DateTimeField(
        verbose_name="Date de début",
        blank=True,
        null=True,
        help_text="Sera affiché si c'est un évènement",
    )
    end_date = models.DateTimeField(
        verbose_name="Date de fin",
        blank=True,
        null=True,
        help_text="Renseigner si différent de la date de début",
    )
    place = models.CharField(
        verbose_name="Lieu",
        max_length=255,
        blank=True,
        help_text="Sera affiché si c'est un évènement",
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    schemes = models.ManyToManyField(
        "home.Scheme", blank=True, verbose_name="Dispositifs reliés"
    )

    search_fields = [
        index.SearchField("name", partial_match=True),
        index.FilterField("publication_date"),
    ]

    panels = [
        FieldPanel("name"),
        FieldPanel("short_description", classname="full"),
        FieldPanel("slug", classname="full"),
        FieldPanel("publication_date"),
        FieldPanel("is_event"),
        FieldPanel("start_date", classname="collapsible"),
        FieldPanel("end_date", classname="collapsible"),
        FieldPanel("place", classname="collapsible"),
        ImageChooserPanel("image"),
        FieldPanel("schemes", widget=forms.CheckboxSelectMultiple),
    ] + FreeBodyField.panels

    def __str__(self):
        return self.name

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Actualités / Evènements"
        verbose_name = "Actualité / Evènement"
        ordering = ["publication_date"]

    def __init__(self, *args, **kwargs):
        """Fixes a bug when trying to translate."""
        if "index_entries" in kwargs:
            kwargs.pop("index_entries")
        super().__init__(*args, **kwargs)


@register_setting
class SocialMediaSettings(BaseSetting):
    facebook = models.URLField(
        help_text="URL de votre page Facebook", blank=True, null=True
    )
    instagram = models.URLField(
        help_text="URL de votre page Instagram", blank=True, null=True
    )
    linkedin = models.URLField(
        help_text="URL de votre page LinkedIn", blank=True, null=True
    )
    youtube = models.URLField(
        help_text="URL de votre page YouTube", blank=True, null=True
    )
    twitter = models.URLField(
        help_text="URL de votre page Twitter", blank=True, null=True
    )

    class Meta:
        verbose_name = "Comptes des réseaux sociaux"


@register_setting
class NewsLetterSettings(BaseSetting):
    newsLetter = models.URLField(
        help_text="Lien d'inscription à la lettre d'information",
        max_length=300,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Inscription à la lettre d'information"
