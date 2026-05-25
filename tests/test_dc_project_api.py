import unittest
from unittest.mock import patch
import requests

from src.entities.dc_project.api import _query_arcgis

class TestDCProjectAPI(unittest.TestCase):

    @patch('src.entities.dc_project.api.requests.get')
    def test_query_arcgis_request_exception(self, mock_get):
        # Setup mock to raise a RequestException
        mock_get.side_effect = requests.RequestException("Mocked network error")

        # Call the function
        result = _query_arcgis(base_url="http://mocked-url")

        # Assert that the function catches the exception and returns an empty list
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
