import sys
import os
import unittest
from unittest.mock import patch, MagicMock, mock_open, ANY

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.shared.utils.inspector import DataInspector

class TestDataInspector(unittest.TestCase):
    def setUp(self):
        self.inspector = DataInspector()

    @patch('src.shared.utils.inspector.os.makedirs')
    @patch('src.shared.utils.inspector.requests.get')
    def test_download_resource_exception(self, mock_get, mock_makedirs):
        # Setup mock exception
        mock_get.side_effect = Exception("Connection dropped")

        # Call method
        path, status = self.inspector.download_resource("http://example.com/data.csv", "data.csv")

        # Verify calls
        mock_makedirs.assert_called_once_with("data/raw", exist_ok=True)
        mock_get.assert_called_once_with(
            "http://example.com/data.csv",
            stream=True,
            headers=ANY,
            timeout=60
        )

        # Verify return value
        self.assertIsNone(path)
        self.assertEqual(status, "FAILED: Connection dropped")

    @patch('src.shared.utils.inspector.os.makedirs')
    @patch('src.shared.utils.inspector.requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_resource_success(self, mock_file, mock_get, mock_makedirs):
        # Setup mock response for successful download
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b'chunk1', b'chunk2']
        mock_get.return_value = mock_response

        # Call method
        path, status = self.inspector.download_resource("http://example.com/data.csv", "data.csv", target_dir="test/dir")

        # Verify calls
        mock_makedirs.assert_called_once_with("test/dir", exist_ok=True)
        mock_get.assert_called_once_with(
            "http://example.com/data.csv",
            stream=True,
            headers=ANY,
            timeout=60
        )

        # Verify file operations
        mock_file.assert_called_once_with("test/dir/data.csv", 'wb')
        mock_file().write.assert_any_call(b'chunk1')
        mock_file().write.assert_any_call(b'chunk2')
        self.assertEqual(mock_file().write.call_count, 2)

        # Verify return value
        self.assertEqual(path, "test/dir/data.csv")
        self.assertEqual(status, "DOWNLOADED")

    @patch('src.shared.utils.inspector.os.makedirs')
    @patch('src.shared.utils.inspector.requests.get')
    def test_download_resource_not_200(self, mock_get, mock_makedirs):
        # Setup mock response for failed download (e.g., 404)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Call method
        path, status = self.inspector.download_resource("http://example.com/data.csv", "data.csv")

        # Verify calls
        mock_makedirs.assert_called_once_with("data/raw", exist_ok=True)

        # Verify return value
        self.assertIsNone(path)
        self.assertEqual(status, "FAILED")

if __name__ == '__main__':
    unittest.main()
