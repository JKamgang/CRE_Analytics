import unittest
from unittest.mock import patch, MagicMock
import sys

# Because our test environment completely lacks standard packages (pandas, numpy, streamlit, requests)
# we are forced to patch them at the `sys.modules` level globally, otherwise the test runner will fail
# to even parse and discover the test files (ImportError). In a real environment with a proper requirements.txt
# installed, this global patching is omitted.

mock_st = MagicMock()
mock_st.cache_data = lambda **kwargs: lambda f: f

# This block checks if pandas exists natively, if not we mock the world
try:
    import pandas
except ImportError:
    sys.modules['streamlit'] = mock_st
    sys.modules['requests'] = MagicMock()
    sys.modules['dotenv'] = MagicMock()
    sys.modules['google'] = MagicMock()
    sys.modules['google.genai'] = MagicMock()
    sys.modules['google.generativeai'] = MagicMock()

    mock_pd = MagicMock()
    mock_pd.DataFrame = MagicMock
    mock_pd.read_csv = MagicMock()
    mock_pd.concat = MagicMock()
    sys.modules['pandas'] = mock_pd

    mock_np = MagicMock()
    sys.modules['numpy'] = mock_np

from src.shared.utils.data_processor import load_or_fetch, load_all_cities, generate_sample_data

class TestDataProcessor(unittest.TestCase):

    @patch('src.shared.utils.data_processor.os.path.exists')
    @patch('src.shared.utils.data_processor.run_dc_pipeline')
    @patch('src.shared.utils.data_processor.pd.read_csv')
    def test_load_or_fetch_existing_file(self, mock_read_csv, mock_run_dc_pipeline, mock_exists):
        # Setup
        mock_exists.return_value = True
        expected_df = MagicMock()
        mock_read_csv.return_value = expected_df

        # Execute
        result = load_or_fetch("DC", force_refresh=False)

        # Assert
        self.assertEqual(result, expected_df)
        mock_read_csv.assert_called_once()
        mock_run_dc_pipeline.assert_not_called()

    @patch('src.shared.utils.data_processor.os.path.exists')
    @patch('src.shared.utils.data_processor.run_dc_pipeline')
    @patch('src.shared.utils.data_processor.pd.read_csv')
    def test_load_or_fetch_missing_file(self, mock_read_csv, mock_run_dc_pipeline, mock_exists):
        # Setup
        mock_exists.return_value = False
        expected_df = MagicMock()
        mock_run_dc_pipeline.return_value = expected_df

        # Execute
        result = load_or_fetch("DC", force_refresh=False)

        # Assert
        self.assertEqual(result, expected_df)
        mock_read_csv.assert_not_called()
        mock_run_dc_pipeline.assert_called_once()

    @patch('src.shared.utils.data_processor.os.path.exists')
    @patch('src.shared.utils.data_processor.run_dc_pipeline')
    @patch('src.shared.utils.data_processor.pd.read_csv')
    def test_load_or_fetch_force_refresh(self, mock_read_csv, mock_run_dc_pipeline, mock_exists):
        # Setup
        mock_exists.return_value = True
        expected_df = MagicMock()
        mock_run_dc_pipeline.return_value = expected_df

        # Execute
        result = load_or_fetch("DC", force_refresh=True)

        # Assert
        self.assertEqual(result, expected_df)
        mock_read_csv.assert_not_called()
        mock_run_dc_pipeline.assert_called_once()

    @patch('src.shared.utils.data_processor.pd.DataFrame')
    @patch('src.shared.utils.data_processor.logger')
    def test_load_or_fetch_unknown_city(self, mock_logger, mock_dataframe):
        # Setup
        expected_df = MagicMock()
        mock_dataframe.return_value = expected_df

        # Execute
        result = load_or_fetch("UNKNOWN", force_refresh=False)

        # Assert
        self.assertEqual(result, expected_df)
        mock_logger.warning.assert_called_once_with("Unknown city: UNKNOWN")

    # City routing tests
    @patch('src.shared.utils.data_processor.os.path.exists')
    @patch('src.shared.utils.data_processor.run_dc_pipeline')
    def test_routing_dc(self, mock_run_pipeline, mock_exists):
        mock_exists.return_value = False
        load_or_fetch("DC")
        mock_run_pipeline.assert_called_once()

    @patch('src.shared.utils.data_processor.os.path.exists')
    @patch('src.shared.utils.data_processor.run_dc_wdcep_pipeline')
    def test_routing_dc_wdcep(self, mock_run_pipeline, mock_exists):
        mock_exists.return_value = False
        load_or_fetch("DC_WDCEP")
        mock_run_pipeline.assert_called_once()

    @patch('src.shared.utils.data_processor.os.path.exists')
    @patch('src.shared.utils.data_processor.run_atlanta_pipeline')
    def test_routing_atlanta(self, mock_run_pipeline, mock_exists):
        mock_exists.return_value = False
        load_or_fetch("ATL")
        mock_run_pipeline.assert_called_once()

    @patch('src.shared.utils.data_processor.os.path.exists')
    @patch('src.shared.utils.data_processor.run_maryland_pipeline')
    def test_routing_maryland(self, mock_run_pipeline, mock_exists):
        mock_exists.return_value = False
        load_or_fetch("MD")
        mock_run_pipeline.assert_called_once()

    @patch('src.shared.utils.data_processor.os.path.exists')
    @patch('src.shared.utils.data_processor.run_ga_metro_pipeline')
    def test_routing_ga_metro(self, mock_run_pipeline, mock_exists):
        mock_exists.return_value = False
        load_or_fetch("GA_METRO")
        mock_run_pipeline.assert_called_once()

    # load_all_cities tests
    @patch('src.shared.utils.data_processor.load_or_fetch')
    @patch('src.shared.utils.data_processor.pd.concat')
    def test_load_all_cities_success(self, mock_concat, mock_load_or_fetch):
        # Setup
        df1 = MagicMock()
        df1.empty = False
        df2 = MagicMock()
        df2.empty = False
        # Mock load_or_fetch to return a valid df on the first two calls, empty on rest
        mock_load_or_fetch.side_effect = [df1, df2, MagicMock(empty=True), MagicMock(empty=True), MagicMock(empty=True)]

        expected_combined = MagicMock()
        mock_concat.return_value = expected_combined

        # Execute
        result = load_all_cities(force_refresh=True)

        # Assert
        self.assertEqual(result, expected_combined)
        mock_concat.assert_called_once_with([df1, df2], ignore_index=True)
        self.assertEqual(mock_load_or_fetch.call_count, 5)

    @patch('src.shared.utils.data_processor.load_or_fetch')
    @patch('src.shared.utils.data_processor.generate_sample_data')
    def test_load_all_cities_empty(self, mock_generate, mock_load_or_fetch):
        # Setup
        # Mock load_or_fetch to return empty dfs for all 5 cities
        mock_load_or_fetch.return_value = MagicMock(empty=True)

        expected_sample = MagicMock()
        mock_generate.return_value = expected_sample

        # Execute
        result = load_all_cities()

        # Assert
        self.assertEqual(result, expected_sample)
        mock_generate.assert_called_once()

if __name__ == '__main__':
    unittest.main()
