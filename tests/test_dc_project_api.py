import unittest
from unittest.mock import patch, MagicMock

from src.entities.dc_project.api import _query_arcgis

class TestDCProjectAPI(unittest.TestCase):
    @patch('src.entities.dc_project.api.requests.get')
    def test_query_arcgis_request_exception(self, mock_get):
        # We want requests.get to raise a RequestException
        import requests
        mock_get.side_effect = requests.RequestException("Simulated Network Error")

        # Call the function
        result = _query_arcgis("http://fakeurl")

        # It should exit cleanly and return an empty list because all_features is empty at start
        self.assertEqual(result, [])
        mock_get.assert_called_once()
