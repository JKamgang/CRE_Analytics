from src.entities.permit.model import Permit
from src.entities.development.model import DevelopmentProject
from src.entities.cremi.model import CREMIIndex

class FloodPressureCalculator:
    """
    Implements the 'Flood Pressure' logic.
    Formula: Permit Intensity + CREMI Delta + Absorption
    """

    def calculate_intensity(self, permits: list[Permit]) -> float:
        # Simplified: total estimated cost of recent permits (normalized)
        total_cost = sum(p.estimated_cost for p in permits if p.estimated_cost)
        return total_cost / 1_000_000 # Normalize to millions

    def calculate_cremi_delta(self, cremi_data: list[CREMIIndex]) -> float:
        if not cremi_data:
            return 0.0
        # Simplistic momentum average
        return sum(c.momentum_score for c in cremi_data) / len(cremi_data)

    def calculate_absorption(self, developments: list[DevelopmentProject]) -> float:
        # Simplified: total square footage of completed/active projects
        total_sqft = sum(d.square_footage for d in developments if d.square_footage)
        return total_sqft / 10_000 # Normalize to 10k sqft units

    def get_pressure_score(self, permits: list[Permit], cremi_data: list[CREMIIndex], developments: list[DevelopmentProject]) -> float:
        intensity = self.calculate_intensity(permits)
        cremi_delta = self.calculate_cremi_delta(cremi_data)
        absorption = self.calculate_absorption(developments)

        # Combining them into a single "Flood Pressure" score
        pressure = (intensity * 0.4) + (cremi_delta * 0.3) + (absorption * 0.3)
        return pressure
