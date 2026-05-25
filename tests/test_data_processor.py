import sys
import unittest
from unittest.mock import patch, MagicMock

# Mock out external dependencies and Streamlit decorators per memory guidelines
sys.modules['pandas'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['streamlit'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['plotly'] = MagicMock()
sys.modules['plotly.express'] = MagicMock()

import streamlit as st
# Mock cache_data as a pass-through to allow testing logic
st.cache_data = lambda **kwargs: lambda f: f

import pandas as pd
import numpy as np
from src.shared.utils.data_processor import (
    load_or_fetch,
    load_all_cities,
    generate_sample_data,
    compute_growth_intensity
)

class TestDataProcessor(unittest.TestCase):

    @patch('src.shared.utils.data_processor.logger')
    @patch('src.shared.utils.data_processor.pd.DataFrame')
    def test_load_or_fetch_unknown_city(self, mock_df, mock_logger):
        # Setup mock for pd.DataFrame()
        mock_empty_df = MagicMock()
        mock_df.return_value = mock_empty_df

        result = load_or_fetch("UNKNOWN")

        # Verify warning was logged
        mock_logger.warning.assert_called_once_with("Unknown city: UNKNOWN")
        # Verify an empty dataframe is returned
        self.assertEqual(result, mock_empty_df)

    @patch('src.shared.utils.data_processor.os.path.exists')
    @patch('src.shared.utils.data_processor.pd.read_csv')
    @patch('src.shared.utils.data_processor.run_dc_pipeline')
    def test_load_or_fetch_file_exists(self, mock_run_pipeline, mock_read_csv, mock_exists):
        mock_exists.return_value = True
        mock_csv_df = MagicMock()
        mock_read_csv.return_value = mock_csv_df

        result = load_or_fetch("DC")

        # Verify os.path.exists was called
        mock_exists.assert_called_once()
        # Verify pd.read_csv was called and its result is returned
        mock_read_csv.assert_called_once()
        self.assertEqual(result, mock_csv_df)
        # Verify pipeline function was not called
        mock_run_pipeline.assert_not_called()

    @patch('src.shared.utils.data_processor.os.path.exists')
    @patch('src.shared.utils.data_processor.run_dc_pipeline')
    def test_load_or_fetch_fallback(self, mock_run_pipeline, mock_exists):
        mock_exists.return_value = False
        mock_pipeline_df = MagicMock()
        mock_run_pipeline.return_value = mock_pipeline_df

        result = load_or_fetch("DC")

        # Verify os.path.exists was called
        mock_exists.assert_called_once()
        # Verify pipeline function was called and its result is returned
        mock_run_pipeline.assert_called_once()
        self.assertEqual(result, mock_pipeline_df)

    @patch('src.shared.utils.data_processor.os.path.exists')
    @patch('src.shared.utils.data_processor.run_dc_pipeline')
    def test_load_or_fetch_force_refresh(self, mock_run_pipeline, mock_exists):
        # Even if exists would return True, it shouldn't be called due to force_refresh
        mock_exists.return_value = True
        mock_pipeline_df = MagicMock()
        mock_run_pipeline.return_value = mock_pipeline_df

        result = load_or_fetch("DC", force_refresh=True)

        # Verify os.path.exists was NOT called
        mock_exists.assert_not_called()
        # Verify pipeline function was called and its result is returned
        mock_run_pipeline.assert_called_once()
        self.assertEqual(result, mock_pipeline_df)

    @patch('src.shared.utils.data_processor.load_or_fetch')
    @patch('src.shared.utils.data_processor.pd.concat')
    def test_load_all_cities(self, mock_concat, mock_load_or_fetch):
        # Create non-empty dummy dataframes
        mock_df = MagicMock()
        mock_df.empty = False
        mock_load_or_fetch.return_value = mock_df

        mock_combined_df = MagicMock()
        mock_concat.return_value = mock_combined_df

        result = load_all_cities()

        # load_or_fetch should be called for each city ("DC", "ATL", "MD", "GA_METRO", "DC_WDCEP")
        self.assertEqual(mock_load_or_fetch.call_count, 5)
        # pd.concat should be called with the list of frames
        mock_concat.assert_called_once()
        self.assertEqual(result, mock_combined_df)

    @patch('src.shared.utils.data_processor.load_or_fetch')
    @patch('src.shared.utils.data_processor.generate_sample_data')
    def test_load_all_cities_fallback(self, mock_generate_sample, mock_load_or_fetch):
        # Create empty dummy dataframes to trigger fallback
        mock_empty_df = MagicMock()
        mock_empty_df.empty = True
        mock_load_or_fetch.return_value = mock_empty_df

        mock_sample_df = MagicMock()
        mock_generate_sample.return_value = mock_sample_df

        result = load_all_cities()

        # generate_sample_data should be called since all loaded dataframes were empty
        mock_generate_sample.assert_called_once()
        self.assertEqual(result, mock_sample_df)

    @patch('src.shared.utils.data_processor.pd.DataFrame')
    def test_generate_sample_data(self, mock_pd_dataframe):
        mock_df = MagicMock()
        mock_pd_dataframe.return_value = mock_df

        result = generate_sample_data()

        mock_pd_dataframe.assert_called_once()
        self.assertEqual(result, mock_df)

    def test_compute_growth_intensity(self):
        mock_df = MagicMock()
        result = compute_growth_intensity(mock_df)
        self.assertEqual(result, mock_df)

if __name__ == '__main__':
    unittest.main()
