from src.shared.api.base_client import ArcGISClient
from src.shared.config.settings import Config
from .model import Permit

class AtlantaPermitAPI:
    def __init__(self):
        # Placeholder ID for Atlanta Building Permits on ARC Open Data
        self.client = ArcGISClient(base_url=Config.ATLANTA_ARC_BASE_URL)

    def fetch_recent_permits(self, limit=100) -> list[Permit]:
        # Using a mock layer ID 0
        data = self.client.fetch_layer_data(layer_id="0", out_fields="*")

        permits = []
        if data and "features" in data:
            for feature in data["features"][:limit]:
                attr = feature.get("attributes", {})
                geom = feature.get("geometry", {})

                permit = Permit(
                    id=str(attr.get("OBJECTID")),
                    permit_type=attr.get("PERMIT_TYPE", "Unknown"),
                    issue_date=str(attr.get("ISSUE_DATE", "")),
                    status=attr.get("STATUS", "Unknown"),
                    estimated_cost=attr.get("ESTIMATED_COST"),
                    description=attr.get("DESCRIPTION"),
                    location={"lat": geom.get("y", 0.0), "lng": geom.get("x", 0.0)}
                )
                permits.append(permit)
        return permits
