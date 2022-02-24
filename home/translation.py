import requests  # type: ignore
from wagtail_localize.machine_translators.deepl import DeepLTranslator, language_code
from wagtail_localize.strings import StringValue


class Translator(DeepLTranslator):
    display_name = "DeepL"

    def translate(self, source_locale, target_locale, strings):
        response = requests.post(
            "https://api-free.deepl.com/v2/translate",
            {
                "auth_key": self.options["AUTH_KEY"],
                "text": [string.data for string in strings],
                "tag_handling": "xml",
                "source_lang": language_code(source_locale.language_code),
                "target_lang": language_code(
                    target_locale.language_code, is_target=True
                ),
            },
        )

        return {
            string: StringValue(translation["text"])
            for string, translation in zip(strings, response.json()["translations"])
        }
