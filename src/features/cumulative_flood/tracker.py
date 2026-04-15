class CumulativeFloodTracker:
    def generate_timeline(self, start_year=2010, end_year=2026, base_pressure=0.0):
        timeline = []
        current_flood_level = base_pressure

        for year in range(start_year, end_year + 1):
            # Simulate year-over-year compounding growth based on pressure
            # In a real scenario, this would use yearly filtered data from entities.
            growth_factor = 1.05 + (current_flood_level * 0.01) # Example compounding logic
            current_flood_level *= growth_factor

            # Add some simulated stochastic variance
            current_flood_level += (year % 3) * 0.5

            timeline.append({
                "year": year,
                "cumulative_flood_level": round(current_flood_level, 2)
            })

        return timeline
