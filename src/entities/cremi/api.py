from .model import CREMIIndex
import random

class CREMIMockAPI:
    """Mock API for Atlanta Fed CREMI Index since it often requires a specific CSV download or an intricate API setup."""
    def fetch_index(self, region="Atlanta", start_year=2010, end_year=2026) -> list[CREMIIndex]:
        indices = []
        for year in range(start_year, end_year + 1):
            for q in range(1, 5):
                # Generating realistic-looking mock data for risk and momentum
                risk = random.uniform(0.1, 0.9)
                momentum = random.uniform(-0.5, 1.5)
                indices.append(CREMIIndex(year=year, quarter=q, region=region, risk_score=risk, momentum_score=momentum))
        return indices
