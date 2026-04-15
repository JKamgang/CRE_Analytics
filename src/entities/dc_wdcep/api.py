import requests
import pandas as pd
import os
from src.shared.config.settings import Config

class QuickbaseClient:
    """
    Step 2: Extraction - Fetches data from DC OCTO Quickbase Portal.
    """
    def __init__(self, realm_hostname="octo.quickbase.com", user_token=None):
        self.base_url = f"https://api.quickbase.com/v1"
        self.headers = {
            "QB-Realm-Hostname": realm_hostname,
            "Authorization": f"QB-USER-TOKEN {user_token}",
            "Content-Type": "application/json"
        }

    def query_records(self, table_id):
        if not self.headers["Authorization"].split()[-1]:
            return pd.DataFrame() # No token provided

        endpoint = f"{self.base_url}/records/query"
        body = {
            "from": table_id,
            "select": [3, 6, 7, 8, 9, 10, 11, 12], # Simulated Field IDs
            "where": "{1.GT.0}" # All records
        }

        try:
            resp = requests.post(endpoint, headers=self.headers, json=body, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            # Transform to DF
            return pd.DataFrame(data.get('data', []))
        except Exception as e:
            print(f"Quickbase Ingestion Failed: {e}")
            return pd.DataFrame()

def run_dc_wdcep_pipeline():
    """Extraction -> Normalization -> Enrichment flow for Quickbase."""
    client = QuickbaseClient(user_token=os.environ.get("QUICKBASE_USER_TOKEN", ""))
    df = client.query_records("bq7id8y2v") # Simulated Master Pipeline Table ID

    if df.empty:
        # Preference 2: Fallback to Download
        from src.shared.utils.inspector import DataInspector
        inspector = DataInspector()
        local_path, status = inspector.download_resource(
            "https://opendata.dc.gov/datasets/dc::wdcep-development-report.csv",
            "wdcep_backup.csv"
        )
        if local_path:
            print(f"Obtained data via: 2-download ({status})")
            df = pd.read_csv(local_path)
        else:
            print("Obtained data via: 4-other (Empty/Sample)")
            return pd.DataFrame()
    else:
        print("Obtained data via: 1-API (Quickbase)")

    return df
