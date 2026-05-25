import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Mock requests before importing DataInspector
if 'requests' not in sys.modules:
    sys.modules['requests'] = MagicMock()

# Add src to path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.shared.utils.inspector import DataInspector

class TestDataInspector(unittest.TestCase):
    def setUp(self):
        self.inspector = DataInspector()

    @patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_api(self, mock_head):
        # Mock response for JSON
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/api")
        self.assertEqual(result, "API")

    @patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_file_csv(self, mock_head):
        # Mock response for CSV
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'text/csv'}
        mock_head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/data.csv")
        self.assertEqual(result, "FILE")

    @patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_file_pdf(self, mock_head):
        # Mock response for PDF
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/doc.pdf")
        self.assertEqual(result, "FILE")

    @patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_unknown(self, mock_head):
        # Mock response for unknown type
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/index.html")
        self.assertEqual(result, "UNKNOWN")

    @patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_no_content_type(self, mock_head):
        # Mock response with no Content-Type header
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/unknown")
        self.assertEqual(result, "UNKNOWN")

    @patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_error(self, mock_head):
        # Mock an exception
        mock_head.side_effect = Exception("Connection Error")

        result = self.inspector.probe_resource("http://example.com/error")
        self.assertEqual(result, "ERROR")

if __name__ == '__main__':
    unittest.main()
