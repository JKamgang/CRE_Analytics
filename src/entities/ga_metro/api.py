import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def fetch_atlanta_metro_regional_data(limit=1000):
    """
    Fetches commercial development data from ARC Open Data Hub (21-County Metro).
    """
    url = "https://opendata.atlantaregional.com/datasets/bb7da4c7962f430ba561526ef1581760_1/FeatureServer/0/query"
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
                df.rename(columns={'RECORD_ID': 'ProjectID', 'DATE_OPENED': 'EntryDate'}, inplace=True)
                df['City'] = 'Atlanta Metro'
            return df
        else:
            logger.warning("No features found in Atlanta Metro ARC API response.")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"Error fetching Atlanta Metro ARC data: {e}")
        return pd.DataFrame()

def run_ga_metro_pipeline():
    logger.info("Running Georgia Metro Pipeline")
    return fetch_atlanta_metro_regional_data()
