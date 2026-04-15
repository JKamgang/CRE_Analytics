from src.entities.permit.api import AtlantaPermitAPI
from src.entities.development.api import DCDevelopmentAPI
from src.entities.cremi.api import CREMIMockAPI
from src.features.growth_status.calculator import GrowthStatusCalculator
from src.features.cumulative_growth_series_series.tracker import CumulativeGrowthSeriesTracker
from src.shared.llm_router import LLMCascadeRouter
import json
import pandas as pd

class DataArteryPipeline:
    def __init__(self):
        self.permit_api = AtlantaPermitAPI()
        self.dev_api = DCDevelopmentAPI()
        self.cremi_api = CREMIMockAPI()

        self.growth_calc = GrowthStatusCalculator()
        self.series_tracker = CumulativeGrowthSeriesTracker()
        self.llm_router = LLMCascadeRouter()

    def run_pipeline(self):
        print("Starting Data Artery Pipeline (Growth Dynamics)...")

        # 1. Fetch Data
        permits = self.permit_api.fetch_recent_permits(limit=50)
        developments = self.dev_api.fetch_projects(limit=50)

        # Convert to DF for logic
        rows = [p.__dict__ for p in permits]
        df = pd.DataFrame(rows)

        # 2. Compute Features
        df = self.growth_calc.calculate_growth_metrics(df)
        base_pressure = df['z_score'].mean() if 'z_score' in df.columns else 0.5

        timeline = self.series_tracker.generate_timeline(base_pressure=base_pressure)

        # 3. Generate LLM Insight
        prompt = f"Analyze Growth Dynamics. Z-Score mean is {base_pressure:.2f}."
        insight = self.llm_router.route_request(prompt)

        return {
            "mean_z_score": round(float(base_pressure), 2),
            "timeline_peak": timeline[-1]['cumulative_growth_series_level'],
            "insight": insight,
            "summary": self.growth_calc.get_status_summary(df)
        }
