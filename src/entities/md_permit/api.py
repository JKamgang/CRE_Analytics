import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def fetch_maryland_permits(limit=1000):
    """
    Fetches commercial building permits for Maryland (e.g., Montgomery, Prince George's Counties)
    using the Maryland iMap ArcGIS portal.
    """
    url = "https://geodata.md.gov/imap/rest/services/BusinessEconomy/MD_IncentiveZones/FeatureServer/0/query"
    params = {
        'where': '1=1',
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
                df.rename(columns={'OBJECTID': 'ProjectID'}, inplace=True)
                df['City'] = 'Maryland'
            return df
        else:
            logger.warning("No features found in Maryland permit API response.")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"Error fetching Maryland permits: {e}")
        return pd.DataFrame()

def run_maryland_pipeline():
    logger.info("Running Maryland Pipeline")
    return fetch_maryland_permits()
