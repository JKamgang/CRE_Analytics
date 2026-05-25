import unittest
from unittest.mock import patch

from src.entities.dc_project.api import _fetch_geojson_fallback
import requests
import pandas as pd

class TestDCApi(unittest.TestCase):

    @patch('src.entities.dc_project.api.requests.get')
    def test_fetch_geojson_fallback_request_exception(self, mock_get):
        # Setup mock to raise a RequestException
        mock_get.side_effect = requests.RequestException("Mocked connection error")

        # Call the function
        result_df = _fetch_geojson_fallback()

        # Assert that the result is an empty DataFrame
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertTrue(result_df.empty)

        # Verify that get was called once with the fallback URL and timeout
        from src.entities.dc_project.api import DC_CONFIG
        mock_get.assert_called_once_with(DC_CONFIG["geojson_url"], timeout=120)

if __name__ == '__main__':
    unittest.main()
