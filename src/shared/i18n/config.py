class I18nConfig:
    LANGUAGES = ["en", "fr", "es"]
    DEFAULT_LANGUAGE = "en"

    TRANSLATIONS = {
        "en": {
            "title": "Alile CRE Analytics",
            "growth_pressure": "Growth Pressure",
            "cumulative_growth": "Cumulative Growth"
        },
        "fr": {
            "title": "Analytique Alile CRE",
            "growth_pressure": "Pression de Croissance",
            "cumulative_growth": "Croissance Cumulée"
        },
        "es": {
            "title": "Análisis Alile CRE",
            "growth_pressure": "Presión de Crecimiento",
            "cumulative_growth": "Crecimiento Acumulado"
        }
    }

    @classmethod
    def get_text(cls, key: str, lang: str = "en") -> str:
        return cls.TRANSLATIONS.get(lang, cls.TRANSLATIONS["en"]).get(key, key)
