import requests
import os

class DataInspector:
    """
    Step 1: Discovery - Probes resources and parses service directories.
    Handles File downloads, API discovery, and PDF parsing for GIS endpoints.
    """
    def probe_resource(self, url):
        try:
            response = requests.head(url, timeout=10)
            content_type = response.headers.get('Content-Type', '').lower()
            if 'application/json' in content_type: return "API"
            if 'text/csv' in content_type or 'application/pdf' in content_type: return "FILE"
            return "UNKNOWN"
        except:
            return "ERROR"

    def download_resource(self, url, filename, target_dir="data/raw"):
        os.makedirs(target_dir, exist_ok=True)
        local_path = os.path.join(target_dir, filename)
        headers = {"User-Agent": "AlileCREAnalytics/2.0 (cs@alileva.com)"}
        try:
            response = requests.get(url, stream=True, headers=headers, timeout=60)
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return local_path, "DOWNLOADED"
        except Exception as e:
            return None, f"FAILED: {e}"
        return None, "FAILED"

    def discovery_agent(self, pdf_path):
        """
        Parses MappingSupport GIS list to find endpoints.
        (Simulated logic for PDF extraction)
        """
        print(f"Scanning {pdf_path} for regional ArcGIS endpoints...")
        return [
            "https://services.arcgis.com/Maryland_Permits/MapServer",
            "https://gis.atlanta.ga/arcgis/rest/services/Zoning/FeatureServer"
        ]
