import sys
import unittest
from unittest.mock import patch, MagicMock

from requests import RequestException
import pandas as pd
from src.entities.dc_project.api import _fetch_geojson_fallback

class TestDCProjectAPI(unittest.TestCase):
    @patch('src.entities.dc_project.api.requests.get')
    def test_fetch_geojson_fallback_request_exception(self, mock_get):
        # We can just use the real RequestException now that requests is installed
        mock_get.side_effect = RequestException("Mocked exception")

        # Configure DataFrame to return a specific mock object when instantiated empty
        # We can patch pandas.DataFrame to return our mock
        with patch('src.entities.dc_project.api.pd.DataFrame') as mock_df_constructor:
            empty_df_mock = MagicMock()
            mock_df_constructor.return_value = empty_df_mock

            # Call function
            result = _fetch_geojson_fallback()

            # Verify empty DataFrame is returned
            self.assertIs(result, empty_df_mock, f"Expected empty_df_mock, got {result}")
            # Verify get was called once
            mock_get.assert_called_once()
            # Verify what get was called with
            args, kwargs = mock_get.call_args
            self.assertIn('timeout', kwargs)

if __name__ == '__main__':
    unittest.main()
