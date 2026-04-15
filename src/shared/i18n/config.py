class I18nConfig:
    LANGUAGES = ["en", "fr", "es"]
    DEFAULT_LANGUAGE = "en"

    TRANSLATIONS = {
        "en": {
            "title": "Alile CRE Analytics",
            "subtitle": "Development Pipeline Visualizer",
            "growth_pressure": "Growth Pressure",
            "cumulative_growth": "Cumulative Growth",
            "data_source": "Data source",
            "language": "Language",
            "tier": "Tier",
            "refresh_data": "🔄 Refresh Data",
            "cities": "Cities",
            "sectors": "Sectors",
            "year_range": "Year range",
            "status": "Status",
            "tab_flood": "🌊 Growth Map",
            "tab_geo": "📍 Geointelligence Map",
            "tab_trends": "📈 Time Series Trends",
            "tab_mf": "🏢 Multifamily Deep-Dive",
            "tab_data": "📋 Data Explorer",
            "tab_exports": "💾 Exports & Scaffolds",
            "tab_learning": "🧠 Learning Hub",
            "login": "👤 User Login / Alile Pay",
            "email": "Email",
            "password": "Password",
            "login_btn": "Login"
        },
        "fr": {
            "title": "Analytique Alile CRE",
            "subtitle": "Visualisateur de pipeline de développement",
            "growth_pressure": "Pression de Croissance",
            "cumulative_growth": "Croissance Cumulée",
            "data_source": "Source de données",
            "language": "Langue",
            "tier": "Niveau",
            "refresh_data": "🔄 Rafraîchir les données",
            "cities": "Villes",
            "sectors": "Secteurs",
            "year_range": "Plage d'années",
            "status": "Statut",
            "tab_flood": "🌊 Carte de Croissance",
            "tab_geo": "📍 Carte de Géo-intelligence",
            "tab_trends": "📈 Tendances Chronologiques",
            "tab_mf": "🏢 Analyse Multifamiliale",
            "tab_data": "📋 Explorateur de Données",
            "tab_exports": "💾 Exportations et Modèles",
            "tab_learning": "🧠 Centre d'Apprentissage",
            "login": "👤 Connexion / Alile Pay",
            "email": "E-mail",
            "password": "Mot de passe",
            "login_btn": "Se connecter"
        },
        "es": {
            "title": "Análisis Alile CRE",
            "subtitle": "Visualizador de Pipeline de Desarrollo",
            "growth_pressure": "Presión de Crecimiento",
            "cumulative_growth": "Crecimiento Acumulado",
            "data_source": "Fuente de datos",
            "language": "Idioma",
            "tier": "Nivel",
            "refresh_data": "🔄 Actualizar Datos",
            "cities": "Ciudades",
            "sectors": "Sectores",
            "year_range": "Rango de años",
            "status": "Estado",
            "tab_flood": "🌊 Mapa de Crecimiento",
            "tab_geo": "📍 Mapa de Geointeligencia",
            "tab_trends": "📈 Tendencias Temporales",
            "tab_mf": "🏢 Análisis Multifamiliar",
            "tab_data": "📋 Explorador de Datos",
            "tab_exports": "💾 Exportaciones y Plantillas",
            "tab_learning": "🧠 Centro de Aprendizaje",
            "login": "👤 Iniciar sesión / Alile Pay",
            "email": "Correo electrónico",
            "password": "Contraseña",
            "login_btn": "Iniciar sesión"
        }
    }

    @classmethod
    def get_text(cls, key: str, lang: str = "en") -> str:
        return cls.TRANSLATIONS.get(lang, cls.TRANSLATIONS["en"]).get(key, key)
