import unittest
import sys

# To run tests without mocking things heavily globally that break pandas, we use patch.dict or do it locally in the test file, but clean up.

from unittest.mock import patch, MagicMock

class TestDCProjectAPI(unittest.TestCase):
    def setUp(self):
        # Apply patch dictionary to mock 'dotenv' and 'streamlit'
        self.mock_modules = patch.dict('sys.modules', {
            'dotenv': MagicMock(),
            'streamlit': MagicMock()
        })
        self.mock_modules.start()

    def tearDown(self):
        self.mock_modules.stop()

    @patch('src.entities.dc_project.api.requests.get')
    @patch('src.entities.dc_project.api.logger')
    def test_query_arcgis_request_exception(self, mock_logger, mock_get):
        import requests
        from src.entities.dc_project.api import _query_arcgis

        # Setup mock to raise a RequestException
        mock_get.side_effect = requests.RequestException("Test exception")

        # Call the function
        result = _query_arcgis("http://fake_base_url")

        # Assert that it returns an empty list
        self.assertEqual(result, [])

        # Assert that get was called once
        mock_get.assert_called_once()

        # Assert that the error was logged
        mock_logger.error.assert_called_once()
        args, _ = mock_logger.error.call_args
        self.assertIn("ArcGIS request failed: %s", args[0])

if __name__ == '__main__':
    unittest.main()
