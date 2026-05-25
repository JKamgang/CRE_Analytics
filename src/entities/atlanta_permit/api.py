"""
Atlanta Data Pipeline — Building Permits
==========================================
Fetches building permit data from the City of Atlanta's ArcGIS Feature Service,
normalizes it to the canonical CRE schema, and exports to CSV.
"""

import os
import logging
import requests
import pandas as pd

from src.shared.config.settings import ATLANTA_CONFIG, RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.shared.utils.security import sanitize_query_param

logger = logging.getLogger(__name__)


# ── ArcGIS REST paging helper ────────────────────────────────────────────────
def _query_arcgis(base_url: str, max_records: int = 2000, state=None, county=None, zip_code=None, street=None) -> list[dict]:
    """Page through an ArcGIS FeatureServer and return all features (with geometry). Supports hyper-granular geospatial search."""
    all_features: list[dict] = []
    offset = 0

    where_clauses = ["1=1"]
    if state: where_clauses.append(f"STATE = '{sanitize_query_param(state)}'")
    if county: where_clauses.append(f"COUNTY LIKE '%{sanitize_query_param(county)}%'")
    if zip_code: where_clauses.append(f"ZIPCODE = '{sanitize_query_param(zip_code)}'")
    if street: where_clauses.append(f"ADDRESS LIKE '%{sanitize_query_param(street)}%'")

    while True:
        params = {
            "where": " AND ".join(where_clauses),
            "outFields": "*",
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": max_records,
            "returnGeometry": "true",
        }
        logger.info("Fetching Atlanta records offset=%d …", offset)
        try:
            resp = requests.get(f"{base_url}/query", params=params, timeout=60)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            logger.error("Atlanta ArcGIS request failed: %s", exc)
            break

        features = data.get("features", [])
        if not features:
            break

        all_features.extend(features)
        logger.info("  → received %d features (total so far: %d)", len(features), len(all_features))

        if len(features) < max_records:
            break
        offset += max_records

    return all_features


# ── Public functions ─────────────────────────────────────────────────────────
def fetch_atlanta_data(**kwargs) -> pd.DataFrame:
    """Fetch raw Atlanta building-permit data and return as DataFrame."""
    features = _query_arcgis(
        ATLANTA_CONFIG["arcgis_feature_server"],
        ATLANTA_CONFIG["max_record_count"],
        **kwargs
    )

    if not features:
        logger.warning("No features returned from Atlanta API — returning empty DataFrame.")
        return pd.DataFrame()

    rows = []
    for f in features:
        attrs = f.get("attributes", {})
        geom = f.get("geometry", {})
        if geom:
            attrs["_lon"] = geom.get("x")
            attrs["_lat"] = geom.get("y")
        rows.append(attrs)

    df = pd.DataFrame(rows)
    logger.info("Atlanta raw DataFrame: %d rows, %d columns", *df.shape)
    return df


def normalize_atlanta_data(df: pd.DataFrame) -> pd.DataFrame:
    """Map raw Atlanta permit columns to the canonical CRE schema."""
    if df.empty:
        return df

    sector_map = ATLANTA_CONFIG["sector_map"]

    def _map_sector(raw_type) -> str:
        if pd.isna(raw_type):
            return "Other"
        key = str(raw_type).strip().lower()
        if key in sector_map:
            return sector_map[key]
        for token, sector in sector_map.items():
            if token in key:
                return sector
        return "Other"

    # Atlanta column names vary — try multiple options
    # Use a pre-calculated map for O(1) lookups instead of nested loops
    col_map = {col.upper(): col for col in df.columns}

    def _col(candidates, default=None):
        for c in candidates:
            match = col_map.get(c.upper())
            if match:
                return df[match]
        return pd.Series(default, index=df.index, dtype="object")

    out = pd.DataFrame()
    out["project_name"] = _col(["PROJECT_NAME", "ProjectName", "PERMIT_NUMBER", "permit_number", "PERMIT_NUM"], "Atlanta Permit")
    out["city"] = "ATL"
    out["ward"] = _col(["DISTRICT", "District", "NPU", "npu"], "")
    out["neighborhood"] = _col(["ADDRESS", "address", "LOCATION", "location"], "")
    out["developer"] = _col(["APPLICANT", "applicant", "CONTRACTOR", "contractor", "OWNER"], "")
    out["architect"] = ""
    out["sector"] = _col(["PERMIT_TYPE", "permit_type", "TYPE", "type", "WORK_TYPE", "PROJECT_TYPE"]).apply(_map_sector)
    out["status"] = _col(["STATUS", "status", "PERMIT_STATUS"], "")
    out["sqft"] = pd.to_numeric(_col(["SQFT", "sqft", "SQUARE_FEET", "TOTAL_SQFT"], 0), errors="coerce")
    out["units"] = pd.to_numeric(_col(["UNITS", "units", "NUM_UNITS"], 0), errors="coerce")
    out["est_value_millions"] = pd.to_numeric(
        _col(["VALUE", "value", "CONSTRUCTION_COST", "ESTIMATED_COST", "VALUATION"], 0), errors="coerce"
    ) / 1_000_000  # permits typically in dollars
    out["est_delivery"] = _col(["COMPLETION_DATE", "completion_date", "EXPIRATION_DATE"], "")

    # Parse year from date columns
    date_col = _col(["ISSUE_DATE", "issue_date", "ISSUED_DATE", "APPLICATION_DATE", "CREATED_DATE", "DATE_ENTERED"])
    out["report_year"] = pd.to_numeric(
        pd.to_datetime(date_col, errors="coerce").dt.year, errors="coerce"
    )

    out["latitude"] = pd.to_numeric(df.get("_lat", _col(["LATITUDE", "latitude", "Y", "y"])), errors="coerce")
    out["longitude"] = pd.to_numeric(df.get("_lon", _col(["LONGITUDE", "longitude", "X", "x"])), errors="coerce")

    out = out.dropna(subset=["project_name"], how="all")
    logger.info("Atlanta normalized DataFrame: %d rows", len(out))
    return out


def save_atlanta_data(raw_df: pd.DataFrame, processed_df: pd.DataFrame) -> tuple[str, str]:
    """Write raw and processed CSVs; return file paths."""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    raw_path = os.path.join(RAW_DATA_DIR, ATLANTA_CONFIG["raw_file"])
    proc_path = os.path.join(PROCESSED_DATA_DIR, ATLANTA_CONFIG["processed_file"])

    raw_df.to_csv(raw_path, index=False)
    processed_df.to_csv(proc_path, index=False)
    logger.info("Saved Atlanta raw → %s", raw_path)
    logger.info("Saved Atlanta processed → %s", proc_path)
    return raw_path, proc_path


def run_atlanta_pipeline(**kwargs) -> pd.DataFrame:
    """End-to-end: fetch → normalize → save → return processed DataFrame."""
    logger.info("═══ Atlanta Pipeline START ═══")
    raw = fetch_atlanta_data(**kwargs)
    processed = normalize_atlanta_data(raw)
    if not processed.empty:
        save_atlanta_data(raw, processed)
    logger.info("═══ Atlanta Pipeline DONE (%d records) ═══", len(processed))
    return processed


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    df = run_atlanta_pipeline()
    print(df.head())
    print(f"\nTotal records: {len(df)}")
