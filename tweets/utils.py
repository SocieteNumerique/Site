from dateutil.parser import parse as dateutil_parse


def create_anchor_start(link, new_popup=True):
    new_popup = ' target="_blank"' if new_popup else ""
    return f'<a href="{link}"{new_popup}>'


def transform_with_indices(text, indices, tranformations):
    return f"{text[: indices[0]]}{tranformations[0]}{text[indices[0]: indices[1]]}{tranformations[1]}{text[indices[1]:]}"


def transform_hastag(text, entity):
    return transform_with_indices(
        text,
        [entity["start"], entity["end"]],
        [
            create_anchor_start(f'https://twitter.com/hashtag/{entity["tag"]}'),
            "</a>",
        ],
    )


def transform_url(text, entity):
    return transform_with_indices(
        text,
        [entity["start"], entity["end"]],
        [
            create_anchor_start(entity["expanded_url"]),
            "</a>",
        ],
    )


def transform_mention(text, entity):
    return transform_with_indices(
        text,
        [entity["start"], entity["end"]],
        [
            create_anchor_start(f'https://twitter.com/{entity["username"]}'),
            "</a>",
        ],
    )


TRANSFORMATIONS = {
    "transform_hastag": transform_hastag,
    "transform_url": transform_url,
    "transform_mention": transform_mention,
}


def transform_text(text, entities):
    new_text = text

    ordered_entities = sorted(
        [
            *[("transform_hastag", entity) for entity in entities.get("hashtags", [])],
            *[("transform_url", entity) for entity in entities.get("urls", [])],
            *[("transform_mention", entity) for entity in entities.get("mentions", [])],
        ],
        key=lambda x: x[1]["end"],
        reverse=True,
    )

    for (function_name, entity) in ordered_entities:
        new_text = TRANSFORMATIONS[function_name](new_text, entity)

    return new_text


def get_item_having_key_bound_to_specific_value(obj, param_key, compared_value):
    return next(x for x in obj if x[param_key] == compared_value)


def get_image_url(tweet, includes):
    if "attachments" in tweet:
        for media_key in tweet["attachments"].get("media_keys", []):
            media = get_item_having_key_bound_to_specific_value(
                includes["media"], "media_key", media_key
            )
            if media["type"] == "photo":
                return media["url"]
    return None


def serialize_tweet(tweet, includes):
    current_tweet = (
        tweet
        if "referenced_tweets" not in tweet
        or tweet["referenced_tweets"][0]["type"] != "retweeted"
        else get_item_having_key_bound_to_specific_value(
            includes["tweets"], "id", tweet["referenced_tweets"][0]["id"]
        )
    )

    author = get_item_having_key_bound_to_specific_value(
        includes["users"], "id", current_tweet["author_id"]
    )
    return {
        "created_at": dateutil_parse(tweet["created_at"]).strftime("%m/%d/%Y"),
        "author": {
            "name": author["name"],
            "username": author["username"],
        },
        "text": transform_text(
            current_tweet["text"], current_tweet.get("entities") or {}
        ),
        "image_url": get_image_url(tweet, includes),
    }
