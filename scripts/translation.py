import json


translations_dictionary = {
    "en": {
        "welcome_message": "Hello and welcome, adventurer, to yet another dungeon!"
    },
    "es": {
        "welcome_message": "¡Hola aventurero, y bienvenido a la mazmorra!"
    }
}


class Translation:
    def __init__(self, language: str = "en"):
        self.language = language
        self.translations = self._load_translations()

    def _load_translations(self) -> None:
        """Load translations from JSON file or dictionary."""
        try:
            with open("scripts/translations.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            # Fallback to a default dictionary if the file doesn't exist.
            return translations_dictionary

    def translate(self, key: str, **kwargs) -> None:
        """Retrieve a translated string, formatting it with optional arguments."""
        try:
            translated_string = self.translations[self.language][key]
            return translated_string.format(**kwargs)
        except KeyError:
            # Fallback  to English if the translation key or language is missing.
            return self.translations["en"].get(key, f"Missing translation: {key}")