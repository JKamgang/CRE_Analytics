import pandas as pd
import numpy as np
import json
import os

class GrowthStatusCalculator:
    """
    Step 4: Enrichment - Calculates Z-Score and maps into Growth Dynamics categories.
    Increase (+): Z > 1
    Stagnation (=): -1 <= Z <= 1
    Decline (-): Z < -1
    """
    def __init__(self):
        self.semantic_map = self._load_semantic_map()

    def _load_semantic_map(self):
        path = "src/shared/models/semantic_map.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def calculate_growth_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        # Preference: Estimated Cost, Fallback: SqFt
        target_col = 'est_value_millions' if 'est_value_millions' in df.columns else 'sqft'

        if target_col in df.columns:
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

        # Semantic mapping enrichment from Quickbase statuses if present
        if 'raw_status' in df.columns:
            status_map = self.semantic_map.get('status_mapping', {})
            df['growth_status_override'] = df['raw_status'].map(status_map)
            df['growth_status'] = df['growth_status_override'].fillna(df['growth_status'])

        return df

    def get_status_summary(self, df: pd.DataFrame) -> dict:
        if 'growth_status' not in df.columns:
            return {}
        return df['growth_status'].value_counts().to_dict()
