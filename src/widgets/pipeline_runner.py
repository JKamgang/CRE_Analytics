from src.entities.permit.api import AtlantaPermitAPI
from src.entities.development.api import DCDevelopmentAPI
from src.entities.cremi.api import CREMIMockAPI
from src.features.flood_pressure.calculator import FloodPressureCalculator
from src.features.cumulative_flood.tracker import CumulativeFloodTracker
from src.features.llm_cascade.router import LLMCascadeRouter
import json

class DataArteryPipeline:
    def __init__(self):
        self.permit_api = AtlantaPermitAPI()
        self.dev_api = DCDevelopmentAPI()
        self.cremi_api = CREMIMockAPI()

        self.pressure_calc = FloodPressureCalculator()
        self.flood_tracker = CumulativeFloodTracker()
        self.llm_router = LLMCascadeRouter()

    def run_pipeline(self):
        print("Starting Data Artery Pipeline...")

        # 1. Fetch Data
        print("Fetching Permits (Atlanta)...")
        permits = self.permit_api.fetch_recent_permits(limit=50)

        print("Fetching Developments (DC)...")
        developments = self.dev_api.fetch_projects(limit=50)

        print("Fetching CREMI Data...")
        cremi_data = self.cremi_api.fetch_index()

        # 2. Compute Features
        print("Calculating Flood Pressure...")
        pressure_score = self.pressure_calc.get_pressure_score(permits, cremi_data, developments)

        print(f"Current Base Flood Pressure: {pressure_score:.2f}")

        print("Generating Cumulative Flood Timeline (2010-2026)...")
        timeline = self.flood_tracker.generate_timeline(base_pressure=max(1.0, pressure_score))

        # 3. Generate LLM Insight
        prompt = f"Analyze this commercial real estate data. The current 'Flood Pressure' score is {pressure_score:.2f}. The projected 2026 cumulative flood level is {timeline[-1]['cumulative_flood_level']}. Explain what this means for a real estate developer looking for growth corridors."
        print("Requesting Insight from LLM Cascade...")
        insight = self.llm_router.route_request(prompt)

        # 4. Assemble Output
        output = {
            "current_pressure": round(pressure_score, 2),
            "timeline": timeline,
            "insight": insight,
            "data_summary": {
                "permits_analyzed": len(permits),
                "developments_analyzed": len(developments),
                "cremi_records_analyzed": len(cremi_data)
            }
        }

        return output
