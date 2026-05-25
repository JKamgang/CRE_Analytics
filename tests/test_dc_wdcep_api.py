import unittest
from unittest.mock import patch
import requests
import pandas as pd
from src.entities.dc_wdcep.api import QuickbaseClient

class TestQuickbaseClient(unittest.TestCase):

    @patch('src.entities.dc_wdcep.api.requests.post')
    def test_query_records_api_failure(self, mock_post):
        # Set the mock to raise a generic Exception (or real RequestException)
        # Since the code catches `Exception`, we can safely just raise an Exception or RequestException.
        mock_post.side_effect = Exception("API Failure")

        # Instantiate QuickbaseClient
        client = QuickbaseClient(user_token="dummy_token")

        # Call query_records
        df = client.query_records("test_table_id")

        # Assert that the returned value is an empty pandas DataFrame using `df.empty`
        self.assertTrue(df.empty)

if __name__ == '__main__':
    unittest.main()
