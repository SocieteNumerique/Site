import requests
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from requests_oauthlib import OAuth1

from django.conf import settings
from tweets.utils import serialize_tweet


@cache_page(3600)
def get_tweets(request):
    auth = OAuth1(
        settings.TWITTER["TWITTER_API_KEYS"],
        settings.TWITTER["TWITTER_API_SECRET_KEYS"],
        settings.TWITTER["TWITTER_API_ACCESS_TOKEN"],
        settings.TWITTER["TWITTER_API_ACCESS_TOKEN_SECRET"],
    )
    twitter_id = settings.TWITTER["TWITTER_ID"]
    url = f"https://api.twitter.com/2/users/{twitter_id}/tweets"
    params = {
        "expansions": "attachments.media_keys,author_id,entities.mentions.username,referenced_tweets.id,referenced_tweets.id.author_id",
        "user.fields": "name,username",
        "media.fields": "url",
        "tweet.fields": "created_at,referenced_tweets,entities",
    }
    result = requests.get(url, auth=auth, params=params).json()

    # NOTE: The usual template/context rendering process is irrelevant
    # here, so we'll just return a HttpResponse directly
    return JsonResponse(
        {
            "tweets": [
                serialize_tweet(tweet, result["includes"]) for tweet in result["data"]
            ]
        }
    )
