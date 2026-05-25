import unittest
from unittest.mock import patch
import pandas as pd
import requests

from src.entities.dc_project.api import _fetch_geojson_fallback

class TestDCProjectAPI(unittest.TestCase):

    @patch('src.entities.dc_project.api.requests.get')
    def test_fetch_geojson_fallback_request_exception(self, mock_get):
        """Test that _fetch_geojson_fallback degrades gracefully on RequestException."""
        # Setup mock to raise the real requests.RequestException
        mock_get.side_effect = requests.RequestException("Mocked network error")

        result = _fetch_geojson_fallback()

        # Verify it returns an empty pandas DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)

        # Verify requests.get was called
        mock_get.assert_called_once()

if __name__ == '__main__':
    unittest.main()
