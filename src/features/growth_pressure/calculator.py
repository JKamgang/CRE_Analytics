import pandas as pd
import numpy as np

class GrowthPressureCalculator:
    """
    Implements Z-Score normalization for Growth Pressure across Atlanta and DC.
    """

    def calculate_pressure(self, atlanta_df: pd.DataFrame, dc_df: pd.DataFrame) -> pd.DataFrame:
        # Simplified implementation of Z-score logic for growth pressure
        if not atlanta_df.empty and 'est_value_millions' in atlanta_df.columns:
            atlanta_df['z_score_cost'] = (atlanta_df['est_value_millions'] - atlanta_df['est_value_millions'].mean()) / atlanta_df['est_value_millions'].std()
            atlanta_df['growth_pressure'] = atlanta_df['z_score_cost'].clip(lower=0)
        else:
            atlanta_df['growth_pressure'] = 0

        if not dc_df.empty and 'sqft' in dc_df.columns:
            dc_df['z_score_sqft'] = (dc_df['sqft'] - dc_df['sqft'].mean()) / dc_df['sqft'].std()
            dc_df['growth_pressure'] = dc_df['z_score_sqft'].clip(lower=0)
        else:
            dc_df['growth_pressure'] = 0

        combined = pd.concat([atlanta_df, dc_df], ignore_index=True)
        return combined
