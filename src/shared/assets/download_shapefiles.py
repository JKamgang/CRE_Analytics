import requests
import os
import logging

logger = logging.getLogger(__name__)
ASSET_DIR = os.path.dirname(os.path.abspath(__file__))

def download_file(url, filename):
    filepath = os.path.join(ASSET_DIR, filename)
    if os.path.exists(filepath):
        logger.info(f"File {filename} already exists.")
        return filepath

    logger.info(f"Downloading {filename}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Successfully downloaded {filename}.")
        return filepath
    except Exception as e:
        logger.error(f"Failed to download {filename}: {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Placeholder URLs - these would point to actual ArcGIS GeoJSON export endpoints
    assets = {
        "dc_wards.geojson": "https://opendata.dc.gov/datasets/0ef47379cbae44e88267c01eaec2ff6a_31.geojson",
        "atlanta_beltline_tad.geojson": "https://opendata.atlantaregional.com/datasets/beltline-tax-allocation-district.geojson",
        "maryland_county_borders.geojson": "https://geodata.md.gov/imap/rest/services/Boundaries/MD_Borders/FeatureServer/1/query?where=1%3D1&outFields=*&f=geojson"
    }

    for filename, url in assets.items():
        download_file(url, filename)
