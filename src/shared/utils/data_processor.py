import os
import logging
import pandas as pd
import numpy as np
import streamlit as st

from src.shared.config.settings import DC_CONFIG, ATLANTA_CONFIG, PROCESSED_DATA_DIR, RAW_DATA_DIR, SECTORS
from src.entities.dc_project.api import run_dc_pipeline
from src.entities.atlanta_permit.api import run_atlanta_pipeline
from src.entities.md_permit.api import run_maryland_pipeline
from src.entities.ga_metro.api import run_ga_metro_pipeline

logger = logging.getLogger(__name__)

@st.cache_data(show_spinner=False)
def load_or_fetch(city: str, force_refresh: bool = False) -> pd.DataFrame:
    if city.upper() in ("DC", "WASHINGTON"):
        cfg = DC_CONFIG
        pipeline_fn = run_dc_pipeline
    elif city.upper() in ("ATL", "ATLANTA"):
        cfg = ATLANTA_CONFIG
        pipeline_fn = run_atlanta_pipeline
    elif city.upper() in ("MD", "MARYLAND"):
        cfg = {"processed_file": "md_pipeline_processed.csv"}
        pipeline_fn = run_maryland_pipeline
    elif city.upper() in ("GA_METRO", "ATLANTA_METRO"):
        cfg = {"processed_file": "ga_metro_pipeline_processed.csv"}
        pipeline_fn = run_ga_metro_pipeline
    else:
        logger.warning(f"Unknown city: {city}")
        return pd.DataFrame()

    if not force_refresh:
        path = os.path.join(PROCESSED_DATA_DIR, cfg.get("processed_file", "unknown.csv"))
        if os.path.exists(path):
            return pd.read_csv(path)

    return pipeline_fn()

@st.cache_data(show_spinner="Loading Growth Dynamics Artery...")
def load_all_cities(force_refresh: bool = False) -> pd.DataFrame:
    frames = []
    for key in ("DC", "ATL", "MD", "GA_METRO"):
        df = load_or_fetch(key, force_refresh=force_refresh)
        if not df.empty:
            frames.append(df)

    if frames:
        combined = pd.concat(frames, ignore_index=True)
    else:
        combined = generate_sample_data()

    return combined

def generate_sample_data() -> pd.DataFrame:
    np.random.seed(42)
    rows = []
    for city, lat, lon in [("DC", 38.9, -77.0), ("ATL", 33.7, -84.3)]:
        for i in range(25):
            sqft = np.random.randint(10000, 1000000)
            rows.append({
                "project_name": f"{city} Project {i}",
                "city": city,
                "ward": str(np.random.randint(1, 9)),
                "sector": np.random.choice(SECTORS),
                "status": "Active",
                "sqft": sqft,
                "est_value_millions": sqft / 100000,
                "report_year": np.random.randint(2018, 2028),
                "latitude": lat + np.random.uniform(-0.1, 0.1),
                "longitude": lon + np.random.uniform(-0.1, 0.1),
            })
    return pd.DataFrame(rows)

from src.features.growth_status.calculator import GrowthStatusCalculator

def compute_growth_intensity(df: pd.DataFrame) -> pd.DataFrame:
    # Legacy wrapper for intensity simulation
    return df # Logic shifted to geo_viz for better temporal control
