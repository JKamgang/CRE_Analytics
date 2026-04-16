import pandas as pd
import numpy as np

class GrowthStatusCalculator:
    """
    Implements Growth Status logic based on Z-Score normalization.
    Categories: Decline (Z < -1), Stagnation (-1 <= Z <= 1), Increase (Z > 1).
    """

    def calculate_growth_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        # Ensure we have a baseline for Z-score (using est_value_millions or sqft)
        target_col = 'est_value_millions' if 'est_value_millions' in df.columns else 'sqft'

        if target_col in df.columns:
            # Handle possible NaNs in target_col
            vals = pd.to_numeric(df[target_col], errors='coerce').fillna(0)
            std_val = vals.std()
            mean_val = vals.mean()

            if pd.notna(std_val) and std_val > 0:
                df['z_score'] = (vals - mean_val) / std_val
            else:
                df['z_score'] = 0.0

            # Growth Status Categorization
            conditions = [
                (df['z_score'] < -1),
                (df['z_score'] >= -1) & (df['z_score'] <= 1),
                (df['z_score'] > 1)
            ]
            choices = ['Decline', 'Stagnation', 'Increase']
            df['growth_status'] = np.select(conditions, choices, default='Stagnation')

        return df

    def get_status_summary(self, df: pd.DataFrame) -> dict:
        if 'growth_status' not in df.columns:
            return {}
        return df['growth_status'].value_counts().to_dict()
