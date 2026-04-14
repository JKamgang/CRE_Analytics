import requests

class BaseAPIClient:
    """Base client for making HTTP requests."""

    def __init__(self, base_url=""):
        self.base_url = base_url

    def get(self, endpoint, params=None, headers=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error fetching from {url}: {e}")
            return None

class ArcGISClient(BaseAPIClient):
    """Client for ArcGIS GeoService APIs."""

    def fetch_layer_data(self, layer_id, where="1=1", out_fields="*", f="json"):
        endpoint = f"/{layer_id}/query"
        params = {
            "where": where,
            "outFields": out_fields,
            "f": f,
            "outSR": "4326"  # Output in WGS84
        }
        return self.get(endpoint, params=params)
