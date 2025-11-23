# log_comparator/localization.py

import json
from pathlib import Path

class Localization:
    def __init__(self, language='en', locales_path='locales'):
        # Inicjalizujemy klasę z gotową, absolutną ścieżką
        self.locales_path = Path(locales_path)
        self.language = language
        self.translations = self._load_translations()

    def _load_translations(self):
        default_lang_path = self.locales_path / 'en.json'
        lang_path = self.locales_path / f'{self.language}.json'
        try:
            with default_lang_path.open('r', encoding='utf-8') as f:
                translations = json.load(f)
            if lang_path.exists() and self.language != 'en':
                with lang_path.open('r', encoding='utf-8') as f:
                    translations.update(json.load(f))
            return translations
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Zwracamy pusty słownik w razie błędu, co spowoduje wyświetlanie kluczy
            print(f"CRITICAL: Could not load translation files from {self.locales_path}. Error: {e}")
            return {}

    def get_string(self, key, **kwargs):
        value = self.translations.get(key, key)
        # Be defensive: formatting may fail if template contains placeholders
        try:
            if isinstance(value, str):
                return value.format(**kwargs)
            return str(value)
        except Exception:
            # Fall back to raw value or key to avoid crashing the UI
            try:
                return str(value)
            except Exception:
                return key

SUPPORTED_LANGUAGES = {
    'en': 'English', 'pl': 'Polski', 'de': 'Deutsch',
    'fr': 'Français', 'es': 'Español', 'pt': 'Português',
}