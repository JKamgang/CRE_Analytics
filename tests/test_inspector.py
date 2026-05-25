import sys
import unittest
from unittest.mock import MagicMock

# Mock requests module since it is not available in the environment
mock_requests = MagicMock()
sys.modules['requests'] = mock_requests

from src.shared.utils.inspector import DataInspector

class TestDataInspector(unittest.TestCase):
    def setUp(self):
        self.inspector = DataInspector()
        mock_requests.reset_mock()
        mock_requests.head.side_effect = None

    def test_probe_resource_api(self):
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'application/json; charset=utf-8'}
        mock_requests.head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/api")
        self.assertEqual(result, "API")
        mock_requests.head.assert_called_once_with("http://example.com/api", timeout=10)

    def test_probe_resource_file_csv(self):
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'text/csv'}
        mock_requests.head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/data.csv")
        self.assertEqual(result, "FILE")

    def test_probe_resource_file_pdf(self):
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_requests.head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/doc.pdf")
        self.assertEqual(result, "FILE")

    def test_probe_resource_unknown(self):
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_requests.head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/")
        self.assertEqual(result, "UNKNOWN")

    def test_probe_resource_error_fallback(self):
        mock_requests.head.side_effect = Exception("Connection error")

        result = self.inspector.probe_resource("http://example.com/error")
        self.assertEqual(result, "ERROR")

if __name__ == '__main__':
    unittest.main()
