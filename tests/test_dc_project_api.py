import sys
import unittest
from unittest.mock import patch, MagicMock

# Environment mocks
import sys
if 'pandas' not in sys.modules:
    sys.modules['pandas'] = MagicMock()
if 'requests' not in sys.modules:
    sys.modules['requests'] = MagicMock()
if 'dotenv' not in sys.modules:
    sys.modules['dotenv'] = MagicMock()
if 'streamlit' not in sys.modules:
    sys.modules['streamlit'] = MagicMock()
if 'google.genai' not in sys.modules:
    sys.modules['google.genai'] = MagicMock()
if 'numpy' not in sys.modules:
    sys.modules['numpy'] = MagicMock()

from src.entities.dc_project.api import fetch_dc_data

class TestDCProjectAPI(unittest.TestCase):

    @patch('src.entities.dc_project.api.requests.get')
    def test_fetch_dc_data_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "features": [
                {"attributes": {"PROJECTNAME": "Test Project 1", "WARD": "Ward 1"}},
                {"attributes": {"PROJECTNAME": "Test Project 2", "WARD": "Ward 2"}}
            ]
        }
        mock_response.raise_for_status.return_value = None

        mock_empty_response = MagicMock()
        mock_empty_response.json.return_value = {"features": []}
        mock_empty_response.raise_for_status.return_value = None

        mock_get.side_effect = [mock_response, mock_empty_response]

        # Call function
        with patch('src.entities.dc_project.api.pd.DataFrame') as mock_df:
            mock_df_instance = MagicMock()
            mock_df.return_value = mock_df_instance

            df = fetch_dc_data()

            self.assertEqual(mock_get.call_count, 1)
            self.assertEqual(df, mock_df_instance)

            # Verify pandas was called correctly
            mock_df.assert_called_once()
            args = mock_df.call_args[0][0]
            self.assertEqual(len(args), 2)
            self.assertEqual(args[0]["PROJECTNAME"], "Test Project 1")

    @patch('src.entities.dc_project.api.requests.get')
    @patch('src.entities.dc_project.api.DC_CONFIG')
    def test_fetch_dc_data_pagination(self, mock_config, mock_get):
        def config_get(k, default=None):
            if k == "max_record_count":
                return 2
            return "http://test.url"

        mock_config.__getitem__.side_effect = config_get
        mock_config.get.side_effect = config_get

        mock_page1 = MagicMock()
        mock_page1.json.return_value = {
            "features": [{"attributes": {"id": 1}}, {"attributes": {"id": 2}}]
        }

        mock_page2 = MagicMock()
        mock_page2.json.return_value = {
            "features": [{"attributes": {"id": 3}}]
        }

        mock_page3 = MagicMock()
        mock_page3.json.return_value = {
            "features": []
        }

        mock_get.side_effect = [mock_page1, mock_page2, mock_page3]

        with patch('src.entities.dc_project.api.pd.DataFrame'):
            fetch_dc_data()

            self.assertEqual(mock_get.call_count, 2)

            args, kwargs1 = mock_get.call_args_list[0]
            self.assertEqual(kwargs1['params']['resultOffset'], 0)

            args, kwargs2 = mock_get.call_args_list[1]
            self.assertEqual(kwargs2['params']['resultOffset'], 2)

    @patch('src.entities.dc_project.api.requests.get')
    def test_fetch_dc_data_hypergranular_search(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"features": []}

        mock_fallback_response = MagicMock()
        mock_fallback_response.json.return_value = {"features": []}

        mock_get.side_effect = [mock_response, mock_fallback_response]

        with patch('src.entities.dc_project.api.pd.DataFrame'):
            fetch_dc_data(state="DC", county="District", zip_code="20001", street="Pennsylvania Ave")

            args, kwargs = mock_get.call_args_list[0]
            params = kwargs.get('params')

            expected_where_clause = "1=1 AND STATE = 'DC' AND COUNTY LIKE '%District%' AND ZIPCODE = '20001' AND ADDRESS LIKE '%Pennsylvania Ave%'"
            self.assertEqual(params['where'], expected_where_clause)

if __name__ == '__main__':
    unittest.main()
