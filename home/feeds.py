from django.contrib.syndication.views import Feed

from home.models import News, NewsListPage
from home.templatetags.scheme_tags import news_page_url


class LatestNewsFeed(Feed):
    title = "News"
    link = "/rss/news"
    description = "Notifications lors de modification ou d'ajout de nouveaux évènement et actualité dans le comtpte de Société Numérique."
    description_template = "feeds/news.html"

    def items(self):
        return News.objects.order_by("-publication_date")[:5]

    def item_title(self, item):
        return item.name

    def item_link(self, item):
        news_list_page = NewsListPage.objects.filter(locale_id=item.locale_id).get()
        return news_page_url(news_list_page, item)

    def get_context_data(self, **kwargs):
        """
        {'obj': item, 'site': current_site} as the super context.
        """
        context = super().get_context_data(**kwargs)
        context["image_url"] = (
            context["site"].domain + context["obj"].image.file.url
            if context["obj"].image
            else None
        )
        context["scheme_names"] = (
            context["obj"].schemes.all().values_list("name", flat=True)
        )
        return context
