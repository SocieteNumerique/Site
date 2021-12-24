from django.template.defaulttags import register


@register.simple_tag()
def scheme_page_url(home_page, scheme):
    url = home_page.url + home_page.specific.reverse_subpage(
        "scheme",
        args=(str(scheme.slug),),
    )
    return url


@register.simple_tag()
def news_page_url(news_list_page, news):
    url = news_list_page.url + news_list_page.reverse_subpage(
        "news",
        args=(str(news.slug),),
    )
    return url


@register.filter
def get_value(dictionary, key):
    return dictionary[key]


@register.filter
def get_values_list(queryset, value):
    return queryset.values_list(value, flat=True)


@register.filter
def show_in_paginator(page_num, paginator_list):
    return (
        paginator_list.paginator.num_pages < 6
        or page_num == 1
        or page_num == paginator_list.paginator.num_pages
        or paginator_list.number - 1 <= page_num <= paginator_list.number + 1
    )


@register.filter
def show_dots_in_paginator(page_num, paginator_list):
    return (
        paginator_list.paginator.num_pages >= 6
        and 1 < page_num < paginator_list.paginator.num_pages
        and (page_num == paginator_list.number + 2 or page_num == 2)
    )
