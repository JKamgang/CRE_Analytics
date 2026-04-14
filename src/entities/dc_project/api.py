"""
DC Data Pipeline — WDCEP Development Report
=============================================
Fetches data from the Open Data DC ArcGIS FeatureServer, normalizes it into
the canonical CRE Flood Graph schema, and exports to CSV.
"""

import os
import json
import logging
import requests
import pandas as pd

from src.shared.config.settings import DC_CONFIG, RAW_DATA_DIR, PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)


# ── ArcGIS REST paging helper ────────────────────────────────────────────────
def _query_arcgis(base_url: str, max_records: int = 2000) -> list[dict]:
    """Page through an ArcGIS FeatureServer and return all features."""
    all_features: list[dict] = []
    offset = 0

    while True:
        params = {
            "where": "1=1",
            "outFields": "*",
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": max_records,
        }
        logger.info("Fetching DC records offset=%d …", offset)
        try:
            resp = requests.get(f"{base_url}/query", params=params, timeout=60)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            logger.error("ArcGIS request failed: %s", exc)
            break

        features = data.get("features", [])
        if not features:
            break

        all_features.extend(features)
        logger.info("  → received %d features (total so far: %d)", len(features), len(all_features))

        # If fewer than page size, we've reached the end
        if len(features) < max_records:
            break
        offset += max_records

    return all_features


# ── Public functions ─────────────────────────────────────────────────────────
def fetch_dc_data() -> pd.DataFrame:
    """Fetch raw WDCEP data and return as DataFrame."""
    features = _query_arcgis(
        DC_CONFIG["arcgis_feature_server"],
        DC_CONFIG["max_record_count"],
    )

    if not features:
        logger.warning("No features returned from DC API — trying GeoJSON fallback.")
        return _fetch_geojson_fallback()

    rows = [f.get("attributes", {}) for f in features]
    df = pd.DataFrame(rows)
    logger.info("DC raw DataFrame: %d rows, %d columns", *df.shape)
    return df


def _fetch_geojson_fallback() -> pd.DataFrame:
    """Fallback: download the full GeoJSON file."""
    try:
        resp = requests.get(DC_CONFIG["geojson_url"], timeout=120)
        resp.raise_for_status()
        geojson = resp.json()
    except requests.RequestException as exc:
        logger.error("GeoJSON fallback also failed: %s", exc)
        return pd.DataFrame()

    rows = []
    for feat in geojson.get("features", []):
        props = feat.get("properties", {})
        geom = feat.get("geometry", {})
        if geom and geom.get("coordinates"):
            coords = geom["coordinates"]
            props["LONGITUDE"] = coords[0]
            props["LATITUDE"] = coords[1]
        rows.append(props)

    df = pd.DataFrame(rows)
    logger.info("DC GeoJSON fallback DataFrame: %d rows, %d columns", *df.shape)
    return df


def normalize_dc_data(df: pd.DataFrame) -> pd.DataFrame:
    """Map raw WDCEP columns to the canonical CRE schema."""
    if df.empty:
        return df

    sector_map = DC_CONFIG["sector_map"]

    def _map_sector(raw_type: str) -> str:
        if pd.isna(raw_type):
            return "Other"
        key = str(raw_type).strip().lower()
        # Try exact match first, then partial
        if key in sector_map:
            return sector_map[key]
        for token, sector in sector_map.items():
            if token in key:
                return sector
        return "Other"

    # Build canonical columns
    out = pd.DataFrame()
    out["project_name"] = df.get("PROJECTNAME", df.get("PROJECT_NAME", pd.Series(dtype="str")))
    out["city"] = "DC"
    out["ward"] = df.get("WARD", pd.Series(dtype="str"))
    out["neighborhood"] = df.get("LOCATION", df.get("ADDRESS", pd.Series(dtype="str")))
    out["developer"] = df.get("DEVELOPER", pd.Series(dtype="str"))
    out["architect"] = df.get("ARCHITECT", pd.Series(dtype="str"))
    out["sector"] = (df.get("PROJECTTYPE", df.get("PROJECT_TYPE", pd.Series(dtype="str")))).apply(_map_sector)
    out["status"] = df.get("STATUS", pd.Series(dtype="str"))
    out["sqft"] = pd.to_numeric(df.get("TYPE_SQFT", df.get("SQFT", pd.Series(dtype="float"))), errors="coerce")
    out["units"] = pd.to_numeric(df.get("UNITS", pd.Series(dtype="float")), errors="coerce")
    out["est_value_millions"] = pd.to_numeric(
        df.get("ESTVALUEINMILLION", df.get("EST_VALUE", pd.Series(dtype="float"))), errors="coerce"
    )
    out["est_delivery"] = df.get("ESTDELIVERY", df.get("EST_DELIVERY", pd.Series(dtype="str")))
    # REPORT_EDITION_YEAR may be a range like "2024-2025" — extract the last (latest) year
    raw_year = df.get("REPORT_EDITION_YEAR", df.get("REPORT_YEAR", pd.Series(dtype="str")))
    def _parse_year(val):
        if pd.isna(val):
            return None
        s = str(val).strip()
        # Try to get last 4-digit year from the string
        import re
        years = re.findall(r'\b((?:19|20)\d{2})\b', s)
        if years:
            return int(years[-1])
        # Try extracting from delivery date (e.g. "Q2 24" → 2024)
        return None
    out["report_year"] = raw_year.apply(_parse_year)

    # Also create a delivery_year from ESTDELIVERY for time series
    est_del = df.get("ESTDELIVERY", df.get("EST_DELIVERY", pd.Series(dtype="str")))
    def _parse_delivery_year(val):
        if pd.isna(val):
            return None
        s = str(val).strip()
        import re
        years = re.findall(r'\b((?:19|20)\d{2})\b', s)
        if years:
            return int(years[-1])
        # Handle "Q2 24" format
        m = re.search(r'(\d{2})$', s)
        if m:
            yr = int(m.group(1))
            return 2000 + yr if yr < 50 else 1900 + yr
        return None
    out["delivery_year"] = est_del.apply(_parse_delivery_year)

    # Use delivery_year as report_year if report_year is missing
    out["report_year"] = out["report_year"].fillna(out["delivery_year"])
    out.drop(columns=["delivery_year"], inplace=True)
    out["latitude"] = pd.to_numeric(df.get("LATITUDE", df.get("Y", pd.Series(dtype="float"))), errors="coerce")
    out["longitude"] = pd.to_numeric(df.get("LONGITUDE", df.get("X", pd.Series(dtype="float"))), errors="coerce")

    out = out.dropna(subset=["project_name"], how="all")
    logger.info("DC normalized DataFrame: %d rows", len(out))
    return out


def save_dc_data(raw_df: pd.DataFrame, processed_df: pd.DataFrame) -> tuple[str, str]:
    """Write raw and processed CSVs; return file paths."""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    raw_path = os.path.join(RAW_DATA_DIR, DC_CONFIG["raw_file"])
    proc_path = os.path.join(PROCESSED_DATA_DIR, DC_CONFIG["processed_file"])

    raw_df.to_csv(raw_path, index=False)
    processed_df.to_csv(proc_path, index=False)
    logger.info("Saved DC raw → %s", raw_path)
    logger.info("Saved DC processed → %s", proc_path)
    return raw_path, proc_path


def run_dc_pipeline() -> pd.DataFrame:
    """End-to-end: fetch → normalize → save → return processed DataFrame."""
    logger.info("═══ DC Pipeline START ═══")
    raw = fetch_dc_data()
    processed = normalize_dc_data(raw)
    if not processed.empty:
        save_dc_data(raw, processed)
    logger.info("═══ DC Pipeline DONE (%d records) ═══", len(processed))
    return processed


# Allow standalone execution
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    df = run_dc_pipeline()
    print(df.head())
    print(f"\nTotal records: {len(df)}")
