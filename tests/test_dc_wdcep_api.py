import unittest
from unittest.mock import patch
import pandas as pd
from src.entities.dc_wdcep.api import QuickbaseClient

class TestQuickbaseClient(unittest.TestCase):
    @patch('src.entities.dc_wdcep.api.requests')
    def test_query_records_no_token_none(self, mock_requests):
        client = QuickbaseClient(user_token=None)

        df = client.query_records("test_table")
        self.assertTrue(df.empty)
        mock_requests.post.assert_not_called()

    @patch('src.entities.dc_wdcep.api.requests')
    def test_query_records_no_token_empty(self, mock_requests):
        client = QuickbaseClient(user_token="")
        df = client.query_records("test_table")
        self.assertTrue(df.empty)
        mock_requests.post.assert_not_called()

if __name__ == '__main__':
    unittest.main()
