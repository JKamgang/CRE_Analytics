import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.entities.dc_wdcep.api import QuickbaseClient

class TestDCWDCEPAPI(unittest.TestCase):

    @patch('src.entities.dc_wdcep.api.requests.post')
    def test_query_records_no_token(self, mock_post):
        # Initialize client with user_token=None
        client = QuickbaseClient(user_token=None)

        # Call query_records
        result = client.query_records("bq7id8y2v")

        # Assert that it returns an empty DataFrame
        self.assertTrue(result.empty)

        # Assert that no API call was made
        mock_post.assert_not_called()

    @patch('src.entities.dc_wdcep.api.requests.post')
    def test_query_records_empty_string_token(self, mock_post):
        # Initialize client with user_token=""
        client = QuickbaseClient(user_token="")

        # Call query_records
        result = client.query_records("bq7id8y2v")

        # Assert that it returns an empty DataFrame
        self.assertTrue(result.empty)

        # Assert that no API call was made
        mock_post.assert_not_called()

if __name__ == '__main__':
    unittest.main()
