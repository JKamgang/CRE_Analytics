import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We need to mock requests before importing DataInspector since it's not installed in the environment
mock_requests = MagicMock()
sys.modules['requests'] = mock_requests

from src.shared.utils.inspector import DataInspector

class TestDataInspector(unittest.TestCase):
    def setUp(self):
        self.inspector = DataInspector()
        mock_requests.reset_mock(side_effect=True)
        mock_requests.head.side_effect = None

    def test_probe_resource_api(self):
        """Test API case (application/json)"""
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'application/json; charset=utf-8'}
        mock_requests.head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/api")
        self.assertEqual(result, "API")
        mock_requests.head.assert_called_with("http://example.com/api", timeout=10)

    def test_probe_resource_file_csv(self):
        """Test FILE case (text/csv)"""
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'text/csv'}
        mock_requests.head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/data.csv")
        self.assertEqual(result, "FILE")
        mock_requests.head.assert_called_with("http://example.com/data.csv", timeout=10)

    def test_probe_resource_file_pdf(self):
        """Test FILE case (application/pdf)"""
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_requests.head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/doc.pdf")
        self.assertEqual(result, "FILE")
        mock_requests.head.assert_called_with("http://example.com/doc.pdf", timeout=10)

    def test_probe_resource_unknown(self):
        """Test UNKNOWN case (other content type like text/html)"""
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_requests.head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/index.html")
        self.assertEqual(result, "UNKNOWN")
        mock_requests.head.assert_called_with("http://example.com/index.html", timeout=10)

    def test_probe_resource_missing_header(self):
        """Test UNKNOWN case when Content-Type is missing"""
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_requests.head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/unknown")
        self.assertEqual(result, "UNKNOWN")
        mock_requests.head.assert_called_with("http://example.com/unknown", timeout=10)

    def test_probe_resource_error(self):
        """Test ERROR case (simulating exception from requests.head)"""
        mock_requests.head.side_effect = Exception("Connection error")

        result = self.inspector.probe_resource("http://example.com/error")
        self.assertEqual(result, "ERROR")
        mock_requests.head.assert_called_with("http://example.com/error", timeout=10)

if __name__ == '__main__':
    unittest.main()
