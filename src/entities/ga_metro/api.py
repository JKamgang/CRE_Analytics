import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def fetch_atlanta_metro_regional_data(limit=1000, state=None, county=None, zip_code=None, street=None):
    """
    Fetches commercial development data from ARC Open Data Hub (21-County Metro).
    Supports hyper-granular geospatial search (State, County, ZIP, Street).
    """
    url = "https://opendata.atlantaregional.com/datasets/655f985f43cc40b4bf2ab7bc73d2169b_1/FeatureServer/0/query"
    fallback_url = "https://www.arcgis.com/sharing/rest/content/items/655f985f43cc40b4bf2ab7bc73d2169b/data"

    where_clauses = ["1=1"]
    if state: where_clauses.append(f"STATE_ABBR = '{state}'")
    if county: where_clauses.append(f"COUNTY LIKE '%{county}%'")
    if zip_code: where_clauses.append(f"ZIPCODE = '{zip_code}'")
    if street: where_clauses.append(f"STREET_NAME LIKE '%{street}%'")

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
        features = None

        if 'features' in data:
            features = [f['attributes'] for f in data['features']]
        else:
            logger.info("Falling back to raw item data URL...")
            fallback_response = requests.get(fallback_url)
            fallback_response.raise_for_status()
            fallback_data = fallback_response.json()
            if 'features' in fallback_data:
                features = [f['attributes'] for f in fallback_data['features']]

        if features:
            df = pd.DataFrame(features)

            # Standardize columns to match Data Artery
            if not df.empty:
                df.rename(columns={'RECORD_ID': 'project_id', 'DATE_OPENED': 'entry_date'}, inplace=True)
                df['city'] = 'GA_METRO'
                df['sector'] = 'Other'
                df['est_value_millions'] = 1.0 # placeholder
                df['sqft'] = 1000 # placeholder
                df['report_year'] = 2026
            return df
        else:
            logger.warning("No features found in Atlanta Metro ARC API response.")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"Error fetching Atlanta Metro ARC data: {e}")
        return pd.DataFrame()

def run_ga_metro_pipeline(**kwargs):
    logger.info("Running Georgia Metro Pipeline")
    return fetch_atlanta_metro_regional_data(**kwargs)
