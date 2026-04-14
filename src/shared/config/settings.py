import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

    # Example Base URLs
    DC_WDCEP_BASE_URL = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Property_and_Land_WebMercator/MapServer"
    ATLANTA_ARC_BASE_URL = "https://services1.arcgis.com/1CfuB83LwE58G5g4/arcgis/rest/services"
