import pandas as pd
import numpy as np

class CumulativeGrowthTracker:
    """
    Time-series logic to map growth from 2010 to 2030 based on Growth Pressure compounding.
    """

    def generate_timeline(self, start_year=2010, end_year=2030, base_pressure=0.0):
        timeline = []
        current_growth_level = base_pressure

        for year in range(start_year, end_year + 1):
            # Simulate compounding growth based on pressure (transmission vector)
            growth_factor = 1.05 + (current_growth_level * 0.02)
            current_growth_level *= growth_factor

            # Stochastic variance
            current_growth_level += (year % 5) * 0.3

            timeline.append({
                "year": year,
                "cumulative_growth_level": round(current_growth_level, 2)
            })

        return pd.DataFrame(timeline)
