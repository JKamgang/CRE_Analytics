import requests
import logging

logger = logging.getLogger(__name__)

class BaseAPIClient:
    """
    Base client for making HTTP requests.
    Fixed OSM 403 errors by adding custom User-Agent.
    """
    def __init__(self, base_url=""):
        self.base_url = base_url
        self.headers = {
            "User-Agent": "AlileCREAnalytics/2.0 (cs@alileva.com) DataDiscoveryEngine/1.0"
        }

    def get(self, endpoint, params=None, headers=None):
        url = f"{self.base_url}{endpoint}"
        actual_headers = self.headers.copy()
        if headers:
            actual_headers.update(headers)

        try:
            response = requests.get(url, params=params, headers=actual_headers, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error fetching from {url}: {e}")
            return None

class ArcGISClient(BaseAPIClient):
    """Client for ArcGIS GeoService APIs."""
    def fetch_layer_data(self, layer_id, where="1=1", out_fields="*", f="json"):
        endpoint = f"/{layer_id}/query"
        params = {
            "where": where,
            "outFields": out_fields,
            "f": f,
            "outSR": "4326"
        }
        return self.get(endpoint, params=params)
