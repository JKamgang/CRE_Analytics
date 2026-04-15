"""
Data Processor — Unified multi-city data dynamics management
=====================================================
Loads cached CSVs or runs live pipelines, merges all cities into one
DataFrame, and provides analysis-ready helper functions.
"""

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

# ── Load / refresh helpers ───────────────────────────────────────────────────
def load_processed_csv(city_config: dict) -> pd.DataFrame:
    """Load a previously-saved processed CSV for the given city."""
    path = os.path.join(PROCESSED_DATA_DIR, city_config["processed_file"])
    if os.path.exists(path):
        df = pd.read_csv(path)
        logger.info("Loaded %d records from %s", len(df), path)
        return df
    return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_or_fetch(city: str, force_refresh: bool = False) -> pd.DataFrame:
    """
    Return processed data for a city.
    Uses cached CSV if available; otherwise runs the live pipeline.
    """
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
        logger.warning("Unknown city: %s", city)
        return pd.DataFrame()

    if not force_refresh:
        df = load_processed_csv(cfg)
        if not df.empty:
            return df

    return pipeline_fn()

@st.cache_data(show_spinner="Loading regional data dynamics artery...")
def load_all_cities(force_refresh: bool = False) -> pd.DataFrame:
    """Load and merge data for all configured cities and regions."""
    frames = []
    for city_key in ("DC", "ATL", "MD", "GA_METRO"):
        df = load_or_fetch(city_key, force_refresh=force_refresh)
        if not df.empty:
            frames.append(df)

    if frames:
        combined = pd.concat(frames, ignore_index=True)
    else:
        combined = generate_sample_data()

    logger.info("Combined DataFrame: %d records", len(combined))
    return combined

def generate_sample_data() -> pd.DataFrame:
    """Generate realistic sample data for demo/fallback."""
    np.random.seed(42)
    rows = []
    for city, count, lat, lon in [("DC", 50, 38.9, -77.0), ("ATL", 50, 33.7, -84.3)]:
        for i in range(count):
            sqft = np.random.randint(10000, 500000)
            rows.append({
                "project_name": f"{city} Project {i}",
                "city": city,
                "ward": str(np.random.randint(1, 9)),
                "neighborhood": f"{city} neighborhood",
                "developer": "Sample Dev",
                "sector": np.random.choice(SECTORS),
                "status": "Planned",
                "sqft": sqft,
                "units": sqft // 1000,
                "est_value_millions": sqft / 100000,
                "report_year": np.random.randint(2015, 2030),
                "latitude": lat + np.random.uniform(-0.1, 0.1),
                "longitude": lon + np.random.uniform(-0.1, 0.1),
            })
    return pd.DataFrame(rows)

def get_summary_metrics(df: pd.DataFrame) -> dict:
    if df.empty: return {}
    return {
        "total_projects": len(df),
        "total_sqft": int(df["sqft"].sum()),
        "total_units": int(df["units"].sum()),
        "total_value_m": round(float(df["est_value_millions"].sum()), 1),
        "sectors": df["sector"].nunique(),
        "cities": df["city"].nunique(),
    }

from src.features.growth_status.calculator import GrowthStatusCalculator
from src.features.cumulative_growth_series.tracker import CumulativeGrowthSeriesTracker

def compute_growth_intensity(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "report_year" not in df.columns:
        return df

    calc = GrowthStatusCalculator()
    df = calc.calculate_growth_metrics(df)
    base_pressure = df['z_score'].mean() if 'z_score' in df.columns else 0.0

    tracker = CumulativeGrowthSeriesTracker()
    timeline_data = tracker.generate_timeline(start_year=2010, end_year=2030, base_pressure=base_pressure)
    timeline_df = pd.DataFrame(timeline_data)
    timeline_df.columns = ["report_year", "growth_level"]

    locations = df[['project_name', 'latitude', 'longitude', 'sector', 'city', 'sqft', 'status', 'est_value_millions', 'growth_status']].drop_duplicates()
    cartesian_df = locations.merge(timeline_df, how='cross')

    if 'z_score' in df.columns:
        cartesian_df = cartesian_df.merge(df[['project_name', 'z_score']].drop_duplicates(), on='project_name', how='left')
        cartesian_df['growth_level'] = cartesian_df['growth_level'] * (1 + cartesian_df['z_score'].fillna(0))

    return cartesian_df
