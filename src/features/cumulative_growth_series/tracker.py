class CumulativeGrowthSeriesTracker:
    """
    Time-series logic to map growth Dynamics from 2010 to 2030.
    """

    def generate_timeline(self, start_year=2010, end_year=2030, base_pressure=0.0):
        timeline = []
        current_growth_level = base_pressure

        for year in range(start_year, end_year + 1):
            # Simulate year-over-year compounding growth dynamics
            growth_factor = 1.05 + (current_growth_level * 0.01)
            current_growth_level *= growth_factor

            # Add some simulated stochastic variance for Alile Dynamics
            current_growth_level += (year % 3) * 0.5

            timeline.append({
                "year": year,
                "cumulative_growth_series_level": round(current_growth_level, 2)
            })

        return timeline
