import unittest
from unittest.mock import patch, MagicMock
import requests

from src.shared.api.base_client import BaseAPIClient, ArcGISClient

class TestBaseAPIClient(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://api.example.com"
        self.client = BaseAPIClient(base_url=self.base_url)

    @patch('src.shared.api.base_client.requests.get')
    def test_get_success(self, mock_get):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Execute
        result = self.client.get("/data")

        # Assert
        self.assertEqual(result, {"status": "success"})
        mock_get.assert_called_once_with(
            f"{self.base_url}/data",
            params=None,
            headers=self.client.headers,
            timeout=60
        )
        mock_response.raise_for_status.assert_called_once()

    @patch('src.shared.api.base_client.requests.get')
    def test_get_with_custom_headers_and_params(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        custom_headers = {"Authorization": "Bearer token"}
        params = {"q": "test"}

        result = self.client.get("/data", params=params, headers=custom_headers)

        expected_headers = self.client.headers.copy()
        expected_headers.update(custom_headers)

        self.assertEqual(result, {"status": "success"})
        mock_get.assert_called_once_with(
            f"{self.base_url}/data",
            params=params,
            headers=expected_headers,
            timeout=60
        )

    @patch('src.shared.api.base_client.requests.get')
    def test_get_request_exception(self, mock_get):
        # Setup mock to raise a RequestException
        mock_get.side_effect = requests.exceptions.RequestException("Timeout")

        # Execute
        result = self.client.get("/data")

        # Assert
        self.assertIsNone(result)

    @patch('src.shared.api.base_client.requests.get')
    def test_get_http_error(self, mock_get):
        # Setup mock response to raise HTTPError when raise_for_status is called
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_get.return_value = mock_response

        # Execute
        result = self.client.get("/data")

        # Assert
        self.assertIsNone(result)

class TestArcGISClient(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://services.arcgis.com"
        self.client = ArcGISClient(base_url=self.base_url)

    @patch.object(BaseAPIClient, 'get')
    def test_fetch_layer_data_defaults(self, mock_get):
        mock_get.return_value = {"features": []}

        layer_id = "123"
        result = self.client.fetch_layer_data(layer_id)

        self.assertEqual(result, {"features": []})

        expected_params = {
            "where": "1=1",
            "outFields": "*",
            "f": "json",
            "outSR": "4326"
        }
        mock_get.assert_called_once_with(f"/{layer_id}/query", params=expected_params)

    @patch.object(BaseAPIClient, 'get')
    def test_fetch_layer_data_custom_params(self, mock_get):
        mock_get.return_value = {"features": []}

        layer_id = "123"
        result = self.client.fetch_layer_data(layer_id, where="STATE='GA'", out_fields="OBJECTID", f="geojson")

        self.assertEqual(result, {"features": []})

        expected_params = {
            "where": "STATE='GA'",
            "outFields": "OBJECTID",
            "f": "geojson",
            "outSR": "4326"
        }
        mock_get.assert_called_once_with(f"/{layer_id}/query", params=expected_params)

if __name__ == '__main__':
    unittest.main()
