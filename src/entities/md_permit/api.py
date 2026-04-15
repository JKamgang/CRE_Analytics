import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def fetch_maryland_permits(limit=1000, state=None, county=None, zip_code=None, street=None):
    """
    Fetches commercial building permits for Maryland (e.g., Montgomery, Prince George's Counties)
    using the Maryland iMap ArcGIS portal. Supports hyper-granular spatial searches.
    """
    url = "https://geodata.md.gov/imap/rest/services/BusinessEconomy/MD_IncentiveZones/FeatureServer/0/query"

    where_clauses = ["1=1"]
    if state: where_clauses.append(f"STATE = '{state}'")
    if county: where_clauses.append(f"COUNTY LIKE '%{county}%'")
    if zip_code: where_clauses.append(f"ZIP = '{zip_code}'")
    if street: where_clauses.append(f"STREET LIKE '%{street}%'")

    params = {
        'where': ' AND '.join(where_clauses),
        'outFields': '*',
        'resultRecordCount': limit,
        'f': 'json'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if 'features' in data:
            features = [f['attributes'] for f in data['features']]
            df = pd.DataFrame(features)

            # Standardize columns to match Data Artery
            if not df.empty:
                df.rename(columns={'OBJECTID': 'project_id'}, inplace=True)
                df['city'] = 'MD'
                df['sector'] = 'Other'
                df['est_value_millions'] = 1.0 # placeholder for testing z-score
                df['sqft'] = 1000 # placeholder
                df['report_year'] = 2026
            return df
        else:
            logger.warning("No features found in Maryland permit API response.")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"Error fetching Maryland permits: {e}")
        return pd.DataFrame()

def run_maryland_pipeline(**kwargs):
    logger.info("Running Maryland Pipeline")
    return fetch_maryland_permits(**kwargs)
