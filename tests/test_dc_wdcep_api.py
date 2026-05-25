import sys
import unittest
from unittest.mock import MagicMock, patch

# Safe fallback for network-restricted environments where imports might fail
try:
    import pandas
except ImportError:
    for mod in ['pandas', 'requests', 'dotenv']:
        if mod not in sys.modules:
            sys.modules[mod] = MagicMock()

from src.entities.dc_wdcep.api import QuickbaseClient, run_dc_wdcep_pipeline

class TestDCWDCEPAPI(unittest.TestCase):

    @patch('src.entities.dc_wdcep.api.pd.DataFrame')
    def test_query_records_no_token(self, mock_df):
        # Instantiate client properly with an empty token
        client = QuickbaseClient(user_token="")
        result = client.query_records("test_table")

        # When token is explicitly designed to fail the check, returns empty DataFrame
        mock_df.assert_called_once_with()
        self.assertEqual(result, mock_df.return_value)

    @patch('src.entities.dc_wdcep.api.pd.DataFrame')
    def test_query_records_none_token(self, mock_df):
        # Instantiate client properly with a None token
        client = QuickbaseClient(user_token=None)
        result = client.query_records("test_table")

        # When token is None, returns empty DataFrame
        mock_df.assert_called_once_with()
        self.assertEqual(result, mock_df.return_value)

    @patch('src.entities.dc_wdcep.api.requests.post')
    @patch('src.entities.dc_wdcep.api.pd.DataFrame')
    def test_query_records_success(self, mock_df, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": [{"id": 1, "status": "Active"}]}
        mock_post.return_value = mock_resp

        client = QuickbaseClient(user_token="valid_token")
        result = client.query_records("test_table")

        expected_endpoint = "https://api.quickbase.com/v1/records/query"
        mock_post.assert_called_once_with(expected_endpoint, headers=client.headers, json={"from": "test_table", "select": [3, 6, 7, 8, 9, 10, 11, 12], "where": "{1.GT.0}"}, timeout=60)

        mock_df.assert_called_once_with([{"id": 1, "status": "Active"}])
        self.assertEqual(result, mock_df.return_value)

    @patch('src.entities.dc_wdcep.api.requests.post')
    @patch('src.entities.dc_wdcep.api.pd.DataFrame')
    def test_query_records_failure(self, mock_df, mock_post):
        mock_post.side_effect = Exception("API Error")

        client = QuickbaseClient(user_token="invalid_token")
        result = client.query_records("test_table")

        mock_post.assert_called_once()
        mock_df.assert_called_once_with()
        self.assertEqual(result, mock_df.return_value)

    @patch('src.entities.dc_wdcep.api.QuickbaseClient.query_records')
    def test_run_dc_wdcep_pipeline_api_success(self, mock_query):
        mock_df = MagicMock()
        mock_df.empty = False
        mock_query.return_value = mock_df

        result = run_dc_wdcep_pipeline()

        self.assertEqual(result, mock_df)
        mock_query.assert_called_once_with("bq7id8y2v")

    @patch('src.entities.dc_wdcep.api.QuickbaseClient.query_records')
    @patch('src.shared.utils.inspector.DataInspector.download_resource')
    @patch('src.entities.dc_wdcep.api.pd.read_csv')
    def test_run_dc_wdcep_pipeline_fallback_success(self, mock_read_csv, mock_download, mock_query):
        mock_empty_df = MagicMock()
        mock_empty_df.empty = True
        mock_query.return_value = mock_empty_df

        mock_download.return_value = ("data/raw/wdcep_backup.csv", "DOWNLOADED")

        mock_fallback_df = MagicMock()
        mock_read_csv.return_value = mock_fallback_df

        result = run_dc_wdcep_pipeline()

        mock_download.assert_called_once_with(
            "https://opendata.dc.gov/datasets/dc::wdcep-development-report.csv",
            "wdcep_backup.csv"
        )
        mock_read_csv.assert_called_once_with("data/raw/wdcep_backup.csv")
        self.assertEqual(result, mock_fallback_df)

    @patch('src.entities.dc_wdcep.api.QuickbaseClient.query_records')
    @patch('src.shared.utils.inspector.DataInspector.download_resource')
    @patch('src.entities.dc_wdcep.api.pd.DataFrame')
    def test_run_dc_wdcep_pipeline_fallback_failure(self, mock_df, mock_download, mock_query):
        mock_empty_df = MagicMock()
        mock_empty_df.empty = True
        mock_query.return_value = mock_empty_df

        mock_download.return_value = (None, "FAILED")

        result = run_dc_wdcep_pipeline()

        mock_download.assert_called_once()
        mock_df.assert_called_once_with()
        self.assertEqual(result, mock_df.return_value)

if __name__ == '__main__':
    unittest.main()
