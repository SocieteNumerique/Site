from django.core.cache import cache
from django.shortcuts import redirect


def clear_cache(request):
    cache.clear()
    return redirect("/fr/")
