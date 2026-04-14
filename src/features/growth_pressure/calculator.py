import pandas as pd
import numpy as np

class GrowthPressureCalculator:
    """
    Implements Z-Score normalization for Growth Pressure across multiple municipal datasets.
    Provides logic to deduplicate and overlay multi-regional 'flooding' hotspots.
    """

    def merge_and_deduplicate(self, dfs: list[pd.DataFrame]) -> pd.DataFrame:
        """
        Merge all dataframes into a single 'Data Artery' and remove duplicates
        using the standardized 'ProjectID' column.
        """
        valid_dfs = [df for df in dfs if not df.empty and 'ProjectID' in df.columns]
        if not valid_dfs:
            return pd.DataFrame()

        combined_df = pd.concat(valid_dfs, ignore_index=True)

        initial_count = len(combined_df)
        combined_df.drop_duplicates(subset=['ProjectID'], keep='first', inplace=True)
        removed = initial_count - len(combined_df)

        print(f"Removed {removed} duplicates based on 'ProjectID'.")
        return combined_df

    def calculate_pressure(self, atlanta_df: pd.DataFrame, dc_df: pd.DataFrame, md_df: pd.DataFrame = None, ga_metro_df: pd.DataFrame = None) -> pd.DataFrame:
        # Step 1: Normalize Dollar Value / Cost arrays where possible
        if not atlanta_df.empty and 'est_value_millions' in atlanta_df.columns:
            atlanta_df['z_score_cost'] = (atlanta_df['est_value_millions'] - atlanta_df['est_value_millions'].mean()) / atlanta_df['est_value_millions'].std()
            atlanta_df['growth_pressure'] = atlanta_df['z_score_cost'].clip(lower=0)
        else:
            atlanta_df['growth_pressure'] = 0
            if not atlanta_df.empty: atlanta_df['ProjectID'] = atlanta_df.index.astype(str) + '_atl'

        if not dc_df.empty and 'sqft' in dc_df.columns:
            dc_df['z_score_sqft'] = (dc_df['sqft'] - dc_df['sqft'].mean()) / dc_df['sqft'].std()
            dc_df['growth_pressure'] = dc_df['z_score_sqft'].clip(lower=0)
        else:
            dc_df['growth_pressure'] = 0
            if not dc_df.empty: dc_df['ProjectID'] = dc_df.index.astype(str) + '_dc'

        if md_df is not None and not md_df.empty:
            md_df['growth_pressure'] = 1.0 # placeholder

        if ga_metro_df is not None and not ga_metro_df.empty:
            ga_metro_df['growth_pressure'] = 1.0 # placeholder

        # Step 2: Merge into the single Data Artery and deduplicate
        dfs_to_merge = [atlanta_df, dc_df]
        if md_df is not None: dfs_to_merge.append(md_df)
        if ga_metro_df is not None: dfs_to_merge.append(ga_metro_df)

        return self.merge_and_deduplicate(dfs_to_merge)
