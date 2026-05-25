import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if 'requests' not in sys.modules:
    import unittest.mock
    mock_requests = unittest.mock.MagicMock()
    mock_requests.exceptions.Timeout = Exception
    mock_requests.exceptions.RequestException = Exception
    sys.modules['requests'] = mock_requests

from src.shared.utils.inspector import DataInspector

class TestDataInspector(unittest.TestCase):
    def setUp(self):
        self.inspector = DataInspector()

    @unittest.mock.patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_api(self, mock_head):
        """Test probe_resource when the URL returns application/json (API)."""
        mock_response = unittest.mock.MagicMock()
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/api")
        self.assertEqual(result, "API")

    @unittest.mock.patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_file_csv(self, mock_head):
        """Test probe_resource when the URL returns text/csv (FILE)."""
        mock_response = unittest.mock.MagicMock()
        mock_response.headers = {'Content-Type': 'text/csv'}
        mock_head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/data.csv")
        self.assertEqual(result, "FILE")

    @unittest.mock.patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_file_pdf(self, mock_head):
        """Test probe_resource when the URL returns application/pdf (FILE)."""
        mock_response = unittest.mock.MagicMock()
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/doc.pdf")
        self.assertEqual(result, "FILE")

    @unittest.mock.patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_unknown(self, mock_head):
        """Test probe_resource when the URL returns an unhandled content type (UNKNOWN)."""
        mock_response = unittest.mock.MagicMock()
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/page")
        self.assertEqual(result, "UNKNOWN")

    @unittest.mock.patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_exception(self, mock_head):
        """Test probe_resource handles exceptions and returns ERROR."""
        mock_head.side_effect = Exception("Connection timed out")

        result = self.inspector.probe_resource("http://example.com/timeout")
        self.assertEqual(result, "ERROR")

if __name__ == '__main__':
    unittest.main()
