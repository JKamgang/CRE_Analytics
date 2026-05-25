import unittest
from unittest.mock import patch, MagicMock
import sys

# Offline environment mock for requests per memory constraints
mock_requests = MagicMock()
class MockRequestException(Exception): pass
mock_requests.exceptions.RequestException = MockRequestException

# Use patch.dict instead of directly modifying sys.modules globally so that it cleans up properly
# Since unittest discover imports files, we'll patch it at the module level for this file
sys.modules['requests'] = mock_requests

from src.shared.api.base_client import BaseAPIClient, ArcGISClient

class TestBaseAPIClient(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://api.example.com"
        self.client = BaseAPIClient(self.base_url)
        self.default_headers = {
            "User-Agent": "AlileCREAnalytics/2.0 (cs@alileva.com) DataDiscoveryEngine/1.0"
        }

    @patch('src.shared.api.base_client.requests.get')
    def test_get_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_get.return_value = mock_response

        endpoint = "/test"
        params = {"key": "value"}

        result = self.client.get(endpoint, params=params)

        expected_url = f"{self.base_url}{endpoint}"
        mock_get.assert_called_once_with(
            expected_url,
            params=params,
            headers=self.default_headers,
            timeout=60
        )
        mock_response.raise_for_status.assert_called_once()
        self.assertEqual(result, {"status": "success"})

    @patch('src.shared.api.base_client.requests.get')
    def test_get_header_injection(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_get.return_value = mock_response

        endpoint = "/test"
        custom_headers = {"Authorization": "Bearer token"}

        self.client.get(endpoint, headers=custom_headers)

        expected_url = f"{self.base_url}{endpoint}"
        expected_headers = self.default_headers.copy()
        expected_headers.update(custom_headers)

        mock_get.assert_called_once_with(
            expected_url,
            params=None,
            headers=expected_headers,
            timeout=60
        )

    @patch('src.shared.api.base_client.requests.get')
    def test_get_exception_handling(self, mock_get):
        mock_get.side_effect = sys.modules['requests'].exceptions.RequestException("Test exception")

        endpoint = "/test"
        result = self.client.get(endpoint)

        self.assertIsNone(result)

class TestArcGISClient(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://arcgis.example.com"
        self.client = ArcGISClient(self.base_url)

    @patch.object(BaseAPIClient, 'get')
    def test_fetch_layer_data(self, mock_get):
        mock_get.return_value = {"features": []}

        layer_id = "71"
        result = self.client.fetch_layer_data(layer_id)

        expected_endpoint = f"/{layer_id}/query"
        expected_params = {
            "where": "1=1",
            "outFields": "*",
            "f": "json",
            "outSR": "4326"
        }

        mock_get.assert_called_once_with(expected_endpoint, params=expected_params)
        self.assertEqual(result, {"features": []})

    @patch.object(BaseAPIClient, 'get')
    def test_fetch_layer_data_custom_params(self, mock_get):
        mock_get.return_value = {"features": []}

        layer_id = "71"
        result = self.client.fetch_layer_data(
            layer_id,
            where="STATE='GA'",
            out_fields="OBJECTID",
            f="geojson"
        )

        expected_endpoint = f"/{layer_id}/query"
        expected_params = {
            "where": "STATE='GA'",
            "outFields": "OBJECTID",
            "f": "geojson",
            "outSR": "4326"
        }

        mock_get.assert_called_once_with(expected_endpoint, params=expected_params)
        self.assertEqual(result, {"features": []})

if __name__ == '__main__':
    unittest.main()
