from src.shared.api.base_client import ArcGISClient
from src.shared.config.settings import Config
from .model import DevelopmentProject

class DCDevelopmentAPI:
    def __init__(self):
        # WDCEP Development Report via DCGIS
        self.client = ArcGISClient(base_url=Config.DC_WDCEP_BASE_URL)

    def fetch_projects(self, limit=100) -> list[DevelopmentProject]:
        # Placeholder layer 71 for WDCEP projects (matching DC_CONFIG in settings)
        data = self.client.fetch_layer_data(layer_id="71", out_fields="*")

        projects = []
        if data and "features" in data:
            for feature in data["features"][:limit]:
                attr = feature.get("attributes", {})
                geom = feature.get("geometry", {})

                proj = DevelopmentProject(
                    id=str(attr.get("OBJECTID")),
                    project_name=attr.get("PROJECT_NAME", "Unknown"),
                    status=attr.get("STATUS", "Unknown"),
                    property_type=attr.get("PROPERTY_TYPE", "Unknown"),
                    square_footage=attr.get("SQ_FT"),
                    completion_year=attr.get("COMPLETION_YEAR"),
                    location={"lat": geom.get("y", 0.0), "lng": geom.get("x", 0.0)}
                )
                projects.append(proj)
        return projects
