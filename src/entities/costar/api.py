"""
CoStar Data Pipeline — PLACEHOLDER
====================================
Stub module for future CoStar API integration.
When CoStar API access is available, implement fetch/normalize/save
following the same pattern as dc_pipeline and atlanta_pipeline.

The canonical output schema is identical:
    project_name, city, ward, neighborhood, developer, architect,
    sector, status, sqft, units, est_value_millions, est_delivery,
    report_year, latitude, longitude
"""

import logging
import pandas as pd

from config import COSTAR_CONFIG

logger = logging.getLogger(__name__)


def run_costar_pipeline(market: str = "DC") -> pd.DataFrame:
    """
    Placeholder — returns empty DataFrame until CoStar API is configured.

    Parameters
    ----------
    market : str
        CoStar market identifier (e.g., "DC", "Atlanta").
    """
    if not COSTAR_CONFIG.get("enabled"):
        logger.info(
            "CoStar integration is disabled. Set COSTAR_CONFIG['enabled'] = True "
            "and provide API credentials to activate."
        )
        return pd.DataFrame()

    # ── Future implementation outline ──
    # 1. Authenticate with CoStar API using COSTAR_API_KEY env var
    # 2. Query /properties endpoint filtered by market + property types
    # 3. Page through results
    # 4. Normalize to canonical schema (same columns as DC/Atlanta)
    # 5. Save raw + processed CSVs
    # 6. Return processed DataFrame

    raise NotImplementedError("CoStar API integration not yet implemented.")
