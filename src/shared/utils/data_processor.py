"""
Data Processor — Unified multi-city data management
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


from src.entities.md_permit.api import run_maryland_pipeline
from src.entities.ga_metro.api import run_ga_metro_pipeline

# ── Mock Configs for new Regions ──────────────────────────────────────────────
MD_CONFIG = {"processed_file": "md_pipeline_processed.csv"}
GA_METRO_CONFIG = {"processed_file": "ga_metro_pipeline_processed.csv"}

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
        cfg = MD_CONFIG
        pipeline_fn = run_maryland_pipeline
    elif city.upper() in ("GA_METRO", "ATLANTA_METRO"):
        cfg = GA_METRO_CONFIG
        pipeline_fn = run_ga_metro_pipeline
    else:
        logger.warning("Unknown city: %s", city)
        return pd.DataFrame()

    if not force_refresh:
        df = load_processed_csv(cfg)
        if not df.empty:
            return df

    # Run live pipeline
    return pipeline_fn()


@st.cache_data(show_spinner="Loading regional data artery...")
def load_all_cities(force_refresh: bool = False) -> pd.DataFrame:
    """Load and merge data for all configured cities and regions."""
    frames = []
    for city_key in ("DC", "ATL", "MD", "GA_METRO"):
        df = load_or_fetch(city_key, force_refresh=force_refresh)
        if not df.empty:
            frames.append(df)
    if frames:
        combined = pd.concat(frames, ignore_index=True)
        logger.info("Combined DataFrame: %d records across %d cities/regions", len(combined), len(frames))
        return combined
    return pd.DataFrame()


# ── Analysis helpers ─────────────────────────────────────────────────────────
def generate_sample_data() -> pd.DataFrame:
    """
    Generate realistic sample data for demonstration purposes when
    API data is unavailable. Uses realistic DC and Atlanta project data.
    """
    np.random.seed(42)

    dc_projects = []
    atl_projects = []

    # DC sample data
    dc_names = [
        "Capitol Crossing Phase II", "The Wharf Phase III", "RIA Development",
        "Union Market District Tower", "St. Elizabeths East Gateway",
        "Walter Reed Town Center", "Buzzard Point Stadium District",
        "Congress Heights Metro Center", "NoMa Central", "Southwest Waterfront Hotel",
        "Georgetown Riverfront Office", "Dupont Circle Mixed-Use", "Navy Yard Residential",
        "H Street Corridor Retail", "Anacostia Arts District", "Tenleytown Tower",
        "Brookland Manor Redevelopment", "McMillan Sand Filtration",
        "Poplar Point Development", "Florida Ave Market Phase IV",
    ]
    dc_sectors_list = ["Office", "Mixed-Use", "Multifamily", "Office", "Mixed-Use",
                       "Mixed-Use", "Multifamily", "Retail", "Office", "Hotel",
                       "Office", "Mixed-Use", "Multifamily", "Retail", "Mixed-Use",
                       "Multifamily", "Multifamily", "Mixed-Use", "Mixed-Use", "Retail"]
    dc_wards = ["2", "6", "5", "5", "8", "4", "6", "8", "6", "6",
                "2", "2", "6", "6", "8", "3", "5", "1", "8", "5"]

    for year in range(2018, 2027):
        n = min(len(dc_names), np.random.randint(8, 16))
        indices = np.random.choice(len(dc_names), n, replace=False)
        for i in indices:
            sqft = np.random.randint(50_000, 1_200_000)
            units = np.random.randint(50, 800) if dc_sectors_list[i] in ("Multifamily", "Mixed-Use") else 0
            dc_projects.append({
                "project_name": dc_names[i],
                "city": "DC",
                "ward": dc_wards[i],
                "neighborhood": f"Ward {dc_wards[i]}",
                "developer": f"DC Developer {np.random.randint(1, 20)}",
                "architect": f"Architect {np.random.randint(1, 10)}",
                "sector": dc_sectors_list[i],
                "status": np.random.choice(["Under Construction", "Planned", "Delivered", "Pre-Construction"]),
                "sqft": sqft,
                "units": units,
                "est_value_millions": round(sqft * np.random.uniform(0.0003, 0.001), 1),
                "est_delivery": f"{year + np.random.randint(0, 3)}",
                "report_year": year,
                "latitude": 38.9072 + np.random.uniform(-0.06, 0.06),
                "longitude": -77.0369 + np.random.uniform(-0.06, 0.06),
            })

    # Atlanta sample data
    atl_names = [
        "Centennial Yards", "Midtown Union", "Ponce City Market Expansion",
        "South Downtown Revitalization", "Westside Paper Development",
        "BeltLine Eastside Trail Mixed-Use", "Atlantic Station Phase III",
        "Buckhead Tower", "Peachtree Center Renovation", "Mercedes-Benz Dist.",
        "Eastside BeltLine Apartments", "Piedmont Heights Office Park",
        "Kirkwood Station", "Old Fourth Ward Lofts", "Inman Park Retail",
        "Decatur Transit Village", "West End Mall Redevelopment",
        "North Avenue MARTA", "Underground Atlanta", "Colony Square Reno",
    ]
    atl_sectors_list = ["Mixed-Use", "Office", "Retail", "Mixed-Use", "Mixed-Use",
                        "Multifamily", "Mixed-Use", "Office", "Office", "Mixed-Use",
                        "Multifamily", "Office", "Multifamily", "Multifamily", "Retail",
                        "Mixed-Use", "Retail", "Multifamily", "Mixed-Use", "Office"]
    atl_districts = ["1", "3", "2", "1", "4", "2", "3", "3", "1", "1",
                     "2", "3", "5", "2", "2", "5", "4", "1", "1", "3"]

    for year in range(2018, 2027):
        n = min(len(atl_names), np.random.randint(6, 14))
        indices = np.random.choice(len(atl_names), n, replace=False)
        for i in indices:
            sqft = np.random.randint(40_000, 900_000)
            units = np.random.randint(40, 600) if atl_sectors_list[i] in ("Multifamily", "Mixed-Use") else 0
            atl_projects.append({
                "project_name": atl_names[i],
                "city": "ATL",
                "ward": atl_districts[i],
                "neighborhood": f"District {atl_districts[i]}",
                "developer": f"ATL Developer {np.random.randint(1, 15)}",
                "architect": f"Architect {np.random.randint(1, 8)}",
                "sector": atl_sectors_list[i],
                "status": np.random.choice(["Under Construction", "Planned", "Delivered", "Pre-Construction"]),
                "sqft": sqft,
                "units": units,
                "est_value_millions": round(sqft * np.random.uniform(0.0002, 0.0008), 1),
                "est_delivery": f"{year + np.random.randint(0, 3)}",
                "report_year": year,
                "latitude": 33.7490 + np.random.uniform(-0.06, 0.06),
                "longitude": -84.3880 + np.random.uniform(-0.06, 0.06),
            })

    df = pd.DataFrame(dc_projects + atl_projects)
    logger.info("Generated %d sample records", len(df))
    return df


def get_summary_metrics(df: pd.DataFrame) -> dict:
    """Compute executive-summary KPIs from the combined dataset."""
    if df.empty:
        return {"total_projects": 0, "total_sqft": 0, "total_units": 0,
                "total_value_m": 0, "sectors": 0, "cities": 0}

    return {
        "total_projects": len(df),
        "total_sqft": int(df["sqft"].sum()),
        "total_units": int(df["units"].sum()),
        "total_value_m": round(float(df["est_value_millions"].sum()), 1),
        "sectors": df["sector"].nunique(),
        "cities": df["city"].nunique(),
    }


def get_yearly_sector_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot table of projects by year × sector."""
    if df.empty or "report_year" not in df.columns:
        return pd.DataFrame()
    return (
        df.groupby(["report_year", "sector"])
        .agg(projects=("project_name", "count"),
             total_sqft=("sqft", "sum"),
             total_units=("units", "sum"),
             total_value_m=("est_value_millions", "sum"))
        .reset_index()
        .sort_values(["report_year", "sector"])
    )


def get_multifamily_deep_dive(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to Multifamily-only records for the dedicated deep-dive section."""
    mf = df[df["sector"] == "Multifamily"].copy()
    return mf


from src.features.growth_pressure.calculator import GrowthPressureCalculator
from src.features.cumulative_growth.tracker import CumulativeGrowthTracker

def compute_flood_intensity(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each year, compute a cumulative 'growth level' simulating development
    activity from 2010 to 2030 based on the CumulativeGrowthTracker.
    """
    if df.empty or "report_year" not in df.columns:
        return df

    # Separate logic temporarily if we need to call calculator
    atl_df = df[df['city'] == 'Atlanta, GA'].copy()
    dc_df = df[df['city'] == 'Washington, DC'].copy()

    # Fallback to short codes
    if atl_df.empty: atl_df = df[df['city'] == 'ATL'].copy()
    if dc_df.empty: dc_df = df[df['city'] == 'DC'].copy()

    calc = GrowthPressureCalculator()
    combined_df = calc.calculate_pressure(atlanta_df=atl_df, dc_df=dc_df)

    # Overwrite generic base
    if not combined_df.empty and 'growth_pressure' in combined_df.columns:
        df = df.merge(combined_df[['project_name', 'growth_pressure']], on='project_name', how='left')
        base_pressure = combined_df['growth_pressure'].mean()
    else:
        base_pressure = 0.0

    tracker = CumulativeGrowthTracker()
    timeline_df = tracker.generate_timeline(start_year=2010, end_year=2030, base_pressure=base_pressure)

    # Map back to report year
    timeline_df.columns = ["report_year", "flood_level"]

    # We need to map the simulated timeline (2010-2030) to all geographic records
    # Create a cartesian product of projects and timeline to simulate the animation frame correctly
    locations = df[['project_name', 'latitude', 'longitude', 'sector', 'city', 'sqft', 'status', 'est_value_millions']].drop_duplicates()
    cartesian_df = locations.merge(timeline_df, how='cross')

    # Optional: We can add a variance or threshold based on individual growth pressure
    if 'growth_pressure' in df.columns:
        cartesian_df = cartesian_df.merge(df[['project_name', 'growth_pressure']].drop_duplicates(), on='project_name', how='left')
        cartesian_df['flood_level'] = cartesian_df['flood_level'] * cartesian_df['growth_pressure'].fillna(1.0)

    return cartesian_df
