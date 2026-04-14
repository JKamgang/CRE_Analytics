"""
CRE Flood Graph — Configuration
================================
Central configuration for API endpoints, sector mappings, and application settings.
Designed to be CoStar-ready: add a COSTAR section when data access is available.
"""

import os

# ─── Application Settings ───────────────────────────────────────────────────────
APP_TITLE = "CRE Flood Graph — Development Pipeline Visualizer"
APP_ICON = "🌊"
DEFAULT_PAGE_LAYOUT = "wide"

# ─── Data Directories ──────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# ─── Sector Definitions ────────────────────────────────────────────────────────
# Canonical sectors used across all data sources
SECTORS = [
    "Office",
    "Retail",
    "Multifamily",
    "Industrial",
    "Hotel",
    "Mixed-Use",
    "Other",
]

SECTOR_COLORS = {
    "Office":       "#1f77b4",
    "Retail":       "#ff7f0e",
    "Multifamily":  "#2ca02c",
    "Industrial":   "#d62728",
    "Hotel":        "#9467bd",
    "Mixed-Use":    "#8c564b",
    "Other":        "#7f7f7f",
}

# ─── DC Data Source (Open Data DC — ArcGIS FeatureServer) ──────────────────────
DC_CONFIG = {
    "name": "Washington, DC",
    "short": "DC",
    "arcgis_feature_server": (
        "https://maps2.dcgis.dc.gov/dcgis/rest/services/"
        "DCGIS_DATA/Property_and_Land_WebMercator/FeatureServer/71"
    ),
    "geojson_url": (
        "https://opendata.dc.gov/api/download/v1/items/"
        "02a4002bf9d542ccba267cfec4aebd7a/geojson?layers=71"
    ),
    "max_record_count": 2000,
    # Mapping from source PROJECT_TYPE values → canonical sectors
    "sector_map": {
        "office":           "Office",
        "retail":           "Retail",
        "residential":      "Multifamily",
        "multifamily":      "Multifamily",
        "apartment":        "Multifamily",
        "condo":            "Multifamily",
        "condominium":      "Multifamily",
        "industrial":       "Industrial",
        "hotel":            "Hotel",
        "hospitality":      "Hotel",
        "mixed":            "Mixed-Use",
        "mixed-use":        "Mixed-Use",
        "mixed use":        "Mixed-Use",
        "education":        "Other",
        "quality of life":  "Other",
    },
    "raw_file": "dc_wdcep_raw.csv",
    "processed_file": "dc_pipeline_processed.csv",
    "center_lat": 38.9072,
    "center_lon": -77.0369,
    "default_zoom": 11,
}

# ─── Atlanta Data Source (Atlanta Open Data / ArcGIS) ─────────────────────────
ATLANTA_CONFIG = {
    "name": "Atlanta, GA",
    "short": "ATL",
    # Atlanta publishes building permits via ArcGIS Feature Layer
    "arcgis_feature_server": (
        "https://services5.arcgis.com/H2e8kXqsqoMRfwtz/arcgis/rest/services/"
        "Building_Permits/FeatureServer/0"
    ),
    "geojson_url": (
        "https://services5.arcgis.com/H2e8kXqsqoMRfwtz/arcgis/rest/services/"
        "Building_Permits/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson&resultRecordCount=2000"
    ),
    "max_record_count": 2000,
    "sector_map": {
        "office":        "Office",
        "commercial":    "Office",
        "retail":        "Retail",
        "residential":   "Multifamily",
        "multifamily":   "Multifamily",
        "apartment":     "Multifamily",
        "condo":         "Multifamily",
        "condominium":   "Multifamily",
        "industrial":    "Industrial",
        "warehouse":     "Industrial",
        "hotel":         "Hotel",
        "hospitality":   "Hotel",
        "mixed":         "Mixed-Use",
        "mixed-use":     "Mixed-Use",
        "mixed use":     "Mixed-Use",
    },
    "raw_file": "atl_permits_raw.csv",
    "processed_file": "atl_pipeline_processed.csv",
    "center_lat": 33.7490,
    "center_lon": -84.3880,
    "default_zoom": 11,
}

# ─── CoStar Placeholder (future integration) ──────────────────────────────────
COSTAR_CONFIG = {
    "name": "CoStar",
    "enabled": False,
    "api_base_url": "https://api.costar.com/",  # placeholder
    "api_key_env_var": "COSTAR_API_KEY",
    "notes": (
        "CoStar integration requires a paid API subscription. "
        "When available, add credentials to environment variables and "
        "set enabled=True. The data_processor module will automatically "
        "pick up CoStar data via the modular pipeline."
    ),
}

# ─── Map Settings ──────────────────────────────────────────────────────────────
MAPBOX_STYLE = "carto-positron"  # free, no token needed
FLOOD_COLOR_SCALE = [
    [0.0, "#f7fbff"],
    [0.2, "#c6dbef"],
    [0.4, "#6baed6"],
    [0.6, "#2171b5"],
    [0.8, "#08519c"],
    [1.0, "#08306b"],
]
