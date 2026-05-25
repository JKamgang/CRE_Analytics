import unittest
from unittest.mock import patch, MagicMock
import sys

# Safely mock requests only for the import of base_client if needed
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    mock_requests = MagicMock()
    class MockRequestException(Exception): pass
    class MockHTTPError(MockRequestException): pass
    mock_requests.exceptions.RequestException = MockRequestException
    mock_requests.exceptions.HTTPError = MockHTTPError
    sys.modules['requests'] = mock_requests

from src.shared.api.base_client import BaseAPIClient, ArcGISClient

if not HAS_REQUESTS:
    # Remove from sys.modules so we don't pollute other tests
    del sys.modules['requests']

    # We must alias the exceptions for patching
    RequestException = MockRequestException
    HTTPError = MockHTTPError
else:
    import requests
    RequestException = requests.exceptions.RequestException
    HTTPError = requests.exceptions.HTTPError

class TestBaseAPIClient(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://api.example.com"
        self.client = BaseAPIClient(base_url=self.base_url)

    @patch('src.shared.api.base_client.requests.get')
    def test_get_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        endpoint = "/test"
        params = {"param1": "value1"}

        result = self.client.get(endpoint, params=params)

        mock_get.assert_called_once_with(
            f"{self.base_url}{endpoint}",
            params=params,
            headers=self.client.headers,
            timeout=60
        )
        self.assertEqual(result, {"key": "value"})

    @patch('src.shared.api.base_client.requests.get')
    def test_get_with_custom_headers(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        endpoint = "/test"
        custom_headers = {"Authorization": "Bearer token"}

        expected_headers = self.client.headers.copy()
        expected_headers.update(custom_headers)

        self.client.get(endpoint, headers=custom_headers)

        mock_get.assert_called_once_with(
            f"{self.base_url}{endpoint}",
            params=None,
            headers=expected_headers,
            timeout=60
        )

    @patch('src.shared.api.base_client.requests.get')
    @patch('src.shared.api.base_client.logger.error')
    def test_get_request_exception(self, mock_logger_error, mock_get):
        mock_get.side_effect = RequestException("Test error")

        endpoint = "/error"
        result = self.client.get(endpoint)

        self.assertIsNone(result)
        mock_logger_error.assert_called_once()
        self.assertTrue(mock_logger_error.call_args[0][0].startswith("API Error fetching from"))

    @patch('src.shared.api.base_client.requests.get')
    @patch('src.shared.api.base_client.logger.error')
    def test_get_raise_for_status_exception(self, mock_logger_error, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = HTTPError("HTTP error")
        mock_get.return_value = mock_response

        endpoint = "/error"
        result = self.client.get(endpoint)

        self.assertIsNone(result)
        mock_logger_error.assert_called_once()
        self.assertTrue(mock_logger_error.call_args[0][0].startswith("API Error fetching from"))

class TestArcGISClient(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://arcgis.example.com"
        self.client = ArcGISClient(base_url=self.base_url)

    @patch.object(BaseAPIClient, 'get')
    def test_fetch_layer_data(self, mock_get):
        mock_get.return_value = {"features": []}

        layer_id = "123"
        where = "STATE = 'GA'"
        out_fields = "ID,NAME"
        f = "geojson"

        result = self.client.fetch_layer_data(
            layer_id=layer_id,
            where=where,
            out_fields=out_fields,
            f=f
        )

        expected_endpoint = f"/{layer_id}/query"
        expected_params = {
            "where": where,
            "outFields": out_fields,
            "f": f,
            "outSR": "4326"
        }

        mock_get.assert_called_once_with(expected_endpoint, params=expected_params)
        self.assertEqual(result, {"features": []})

    @patch.object(BaseAPIClient, 'get')
    def test_fetch_layer_data_defaults(self, mock_get):
        mock_get.return_value = {"features": []}

        layer_id = "123"

        result = self.client.fetch_layer_data(layer_id=layer_id)

        expected_endpoint = f"/{layer_id}/query"
        expected_params = {
            "where": "1=1",
            "outFields": "*",
            "f": "json",
            "outSR": "4326"
        }

        mock_get.assert_called_once_with(expected_endpoint, params=expected_params)
        self.assertEqual(result, {"features": []})
