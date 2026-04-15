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
        # Generate dummy Project IDs if missing to ensure data isn't dropped entirely during dedup
        if not atlanta_df.empty:
            if 'project_id' not in atlanta_df.columns:
                atlanta_df['ProjectID'] = atlanta_df.index.astype(str) + '_atl'
            else:
                atlanta_df['ProjectID'] = atlanta_df['project_id'].astype(str) + '_atl'

        if not dc_df.empty:
            if 'project_id' not in dc_df.columns:
                dc_df['ProjectID'] = dc_df.index.astype(str) + '_dc'
            else:
                dc_df['ProjectID'] = dc_df['project_id'].astype(str) + '_dc'

        if md_df is not None and not md_df.empty:
            if 'project_id' not in md_df.columns:
                md_df['ProjectID'] = md_df.index.astype(str) + '_md'
            else:
                md_df['ProjectID'] = md_df['project_id'].astype(str) + '_md'

        if ga_metro_df is not None and not ga_metro_df.empty:
            if 'project_id' not in ga_metro_df.columns:
                ga_metro_df['ProjectID'] = ga_metro_df.index.astype(str) + '_ga'
            else:
                ga_metro_df['ProjectID'] = ga_metro_df['project_id'].astype(str) + '_ga'

        # Step 1: Normalize Dollar Value / Cost arrays where possible
        if not atlanta_df.empty and 'est_value_millions' in atlanta_df.columns:
            std_val = atlanta_df['est_value_millions'].std()
            if pd.notna(std_val) and std_val > 0:
                atlanta_df['z_score_cost'] = (atlanta_df['est_value_millions'] - atlanta_df['est_value_millions'].mean()) / std_val
                atlanta_df['growth_pressure'] = atlanta_df['z_score_cost'].clip(lower=0)
            else:
                atlanta_df['growth_pressure'] = 0.5
        elif not atlanta_df.empty:
            atlanta_df['growth_pressure'] = 0.0

        if not dc_df.empty and 'sqft' in dc_df.columns:
            std_val = dc_df['sqft'].std()
            if pd.notna(std_val) and std_val > 0:
                dc_df['z_score_sqft'] = (dc_df['sqft'] - dc_df['sqft'].mean()) / std_val
                dc_df['growth_pressure'] = dc_df['z_score_sqft'].clip(lower=0)
            else:
                dc_df['growth_pressure'] = 0.5
        elif not dc_df.empty:
            dc_df['growth_pressure'] = 0.0

        if md_df is not None and not md_df.empty:
            md_df['growth_pressure'] = 1.0 # placeholder

        if ga_metro_df is not None and not ga_metro_df.empty:
            ga_metro_df['growth_pressure'] = 1.0 # placeholder

        # Step 2: Merge into the single Data Artery and deduplicate
        dfs_to_merge = [atlanta_df, dc_df]
        if md_df is not None: dfs_to_merge.append(md_df)
        if ga_metro_df is not None: dfs_to_merge.append(ga_metro_df)

        return self.merge_and_deduplicate(dfs_to_merge)
