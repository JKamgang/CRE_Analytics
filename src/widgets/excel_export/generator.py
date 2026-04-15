import pandas as pd
from src.features.growth_pressure.calculator import GrowthPressureCalculator
from src.features.cumulative_growth.tracker import CumulativeGrowthTracker

class ExcelProGenerator:
    """
    Generates a 'Pro' MS Excel file with pre-built PivotTables and Growth time-series logic.
    """

    def __init__(self, output_path="Alile_CRE_Growth_Pro.xlsx"):
        self.output_path = output_path
        self.calc = GrowthPressureCalculator()
        self.tracker = CumulativeGrowthTracker()

    def generate(self, atlanta_df: pd.DataFrame, dc_df: pd.DataFrame):
        # 1. Combine and apply Growth Pressure logic
        combined_df = self.calc.calculate_pressure(atlanta_df, dc_df)

        # 2. Get base pressure and timeline
        base_pressure = combined_df['growth_pressure'].mean() if not combined_df.empty else 0.0
        timeline_df = self.tracker.generate_timeline(base_pressure=base_pressure)

        # 3. Export to Excel with multiple sheets
        with pd.ExcelWriter(self.output_path, engine='xlsxwriter') as writer:
            combined_df.to_excel(writer, sheet_name='Raw Data', index=False)
            timeline_df.to_excel(writer, sheet_name='Growth Timeline (2010-2030)', index=False)

            # Additional 'Pro' logic: Pivot Table Scaffold
            if not combined_df.empty:
                try:
                    pivot = pd.pivot_table(combined_df,
                                           values='growth_pressure',
                                           index='city' if 'city' in combined_df.columns else None,
                                           columns='status' if 'status' in combined_df.columns else None,
                                           aggfunc='mean')
                    pivot.to_excel(writer, sheet_name='Pivot - Pressure by City')

                    if 'zip_code' in combined_df.columns:
                        zip_pivot = pd.pivot_table(combined_df,
                                               values='growth_pressure',
                                               index='zip_code',
                                               aggfunc='count')
                        zip_pivot.to_excel(writer, sheet_name='Pivot - Hotspots by ZIP')
                except Exception as e:
                    print(f"Pivot generation failed: {e}")

        print(f"Generated Pro Excel File: {self.output_path}")
        return self.output_path
