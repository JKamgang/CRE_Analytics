import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# Add src to path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Network-restricted environment mock for requests and other external deps
import unittest.mock
unittest.mock.patch.dict(sys.modules, {
    'requests': MagicMock()
}).start()

from src.shared.utils.inspector import DataInspector

class TestDataInspector(unittest.TestCase):
    def setUp(self):
        self.inspector = DataInspector()

    @patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_api(self, mock_head):
        mock_response = MagicMock()
        mock_response.headers.get.return_value = 'application/json'
        mock_head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/api")
        self.assertEqual(result, "API")

    @patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_file_csv(self, mock_head):
        mock_response = MagicMock()
        mock_response.headers.get.return_value = 'text/csv'
        mock_head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/data.csv")
        self.assertEqual(result, "FILE")

    @patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_file_pdf(self, mock_head):
        mock_response = MagicMock()
        mock_response.headers.get.return_value = 'application/pdf'
        mock_head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com/doc.pdf")
        self.assertEqual(result, "FILE")

    @patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_unknown(self, mock_head):
        mock_response = MagicMock()
        mock_response.headers.get.return_value = 'text/html'
        mock_head.return_value = mock_response

        result = self.inspector.probe_resource("http://example.com")
        self.assertEqual(result, "UNKNOWN")

    @patch('src.shared.utils.inspector.requests.head')
    def test_probe_resource_error(self, mock_head):
        mock_head.side_effect = Exception("Connection Error")

        result = self.inspector.probe_resource("http://example.com")
        self.assertEqual(result, "ERROR")

    @patch('src.shared.utils.inspector.os.makedirs')
    @patch('src.shared.utils.inspector.requests.get')
    def test_download_resource_success(self, mock_get, mock_makedirs):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b'data_chunk']
        mock_get.return_value = mock_response

        with patch('builtins.open', mock_open()) as mocked_file:
            path, status = self.inspector.download_resource("http://example.com/file.zip", "file.zip")

            mock_makedirs.assert_called_once_with("data/raw", exist_ok=True)
            mocked_file.assert_called_once_with(os.path.join("data/raw", "file.zip"), 'wb')
            mocked_file().write.assert_called_once_with(b'data_chunk')
            self.assertEqual(status, "DOWNLOADED")
            self.assertEqual(path, os.path.join("data/raw", "file.zip"))

    @patch('src.shared.utils.inspector.os.makedirs')
    @patch('src.shared.utils.inspector.requests.get')
    def test_download_resource_failed_status(self, mock_get, mock_makedirs):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        path, status = self.inspector.download_resource("http://example.com/file.zip", "file.zip")

        self.assertEqual(status, "FAILED")
        self.assertIsNone(path)

    @patch('src.shared.utils.inspector.os.makedirs')
    @patch('src.shared.utils.inspector.requests.get')
    def test_download_resource_exception(self, mock_get, mock_makedirs):
        mock_get.side_effect = Exception("Network timeout")

        path, status = self.inspector.download_resource("http://example.com/file.zip", "file.zip")

        self.assertEqual(status, "FAILED: Network timeout")
        self.assertIsNone(path)

    @patch('builtins.print')
    def test_discovery_agent(self, mock_print):
        result = self.inspector.discovery_agent("dummy_path.pdf")

        mock_print.assert_called_once_with("Scanning dummy_path.pdf for regional ArcGIS endpoints...")
        self.assertEqual(result, [
            "https://services.arcgis.com/Maryland_Permits/MapServer",
            "https://gis.atlanta.ga/arcgis/rest/services/Zoning/FeatureServer"
        ])

if __name__ == '__main__':
    unittest.main()
