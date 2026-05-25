import sys
import unittest
from unittest.mock import patch, MagicMock

# The user explicitly asked in the memory instructions to mock missing standard libraries
# for tests where network limitations apply using patch.dict(sys.modules, ...) or manual sys.modules assignment.
# We will use manual sys.modules assignment but safely store original states so we can restore them,
# although here we only care about `tests_dc_project_api.py` running successfully without poisoning the environment.

class MockRequestException(Exception):
    pass

class MockRequests(MagicMock):
    RequestException = MockRequestException

mock_requests = MockRequests()
mock_pandas = MagicMock()
mock_dotenv = MagicMock()
mock_numpy = MagicMock()
mock_google_genai = MagicMock()
mock_streamlit = MagicMock()

# Instead of mutating the global sys.modules, we'll let the user's setup handle other files
# since the memory context states they will use mock in tests requiring it.
# We will patch them inside setUp so `api.py` gets the mocks when imported if it's imported dynamically.
# However, python files are imported at test discovery time.
# If we don't mock it globally before discovery, discovery will fail if `api.py` isn't mockable.
# The previous solution failed because we deleted the mocked modules from sys.modules during discovery, breaking other tests that needed them but couldn't import them.

# So the correct approach requested by memory is to just manually assign them to sys.modules at the top of the test file
# because `pip install` fails in this environment.

sys.modules.setdefault('pandas', mock_pandas)
sys.modules.setdefault('requests', mock_requests)
sys.modules.setdefault('dotenv', mock_dotenv)
sys.modules.setdefault('numpy', mock_numpy)
sys.modules.setdefault('google.genai', mock_google_genai)
sys.modules.setdefault('streamlit', mock_streamlit)

from src.entities.dc_project.api import fetch_dc_data, _query_arcgis, _fetch_geojson_fallback

class TestDCProjectAPI(unittest.TestCase):

    @patch('src.entities.dc_project.api.requests.get')
    def test_query_arcgis_success(self, mock_get):
        """Test _query_arcgis correctly paginates and returns all features"""
        mock_response_1 = MagicMock()
        mock_response_1.json.return_value = {"features": [{"attributes": {"id": 1}}, {"attributes": {"id": 2}}]}
        mock_response_2 = MagicMock()
        mock_response_2.json.return_value = {"features": [{"attributes": {"id": 3}}]}

        mock_get.side_effect = [mock_response_1, mock_response_2]

        features = _query_arcgis("http://fake-url", max_records=2)

        self.assertEqual(len(features), 3)
        self.assertEqual(mock_get.call_count, 2)

        args_1, kwargs_1 = mock_get.call_args_list[0]
        self.assertEqual(args_1[0], "http://fake-url/query")
        self.assertEqual(kwargs_1['params']['resultOffset'], 0)
        self.assertEqual(kwargs_1['params']['resultRecordCount'], 2)

        args_2, kwargs_2 = mock_get.call_args_list[1]
        self.assertEqual(kwargs_2['params']['resultOffset'], 2)
        self.assertEqual(kwargs_2['params']['resultRecordCount'], 2)

    @patch('src.entities.dc_project.api.requests.get')
    def test_query_arcgis_filtering(self, mock_get):
        """Test _query_arcgis correctly applies state, county, zip, and street filters"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"features": [{"attributes": {"id": 1}}]}
        mock_get.return_value = mock_response

        features = _query_arcgis(
            "http://fake-url",
            max_records=2,
            state="DC",
            county="District",
            zip_code="20001",
            street="Pennsylvania"
        )

        args, kwargs = mock_get.call_args
        where_clause = kwargs['params']['where']

        self.assertIn("1=1", where_clause)
        self.assertIn("STATE = 'DC'", where_clause)
        self.assertIn("COUNTY LIKE '%District%'", where_clause)
        self.assertIn("ZIPCODE = '20001'", where_clause)
        self.assertIn("ADDRESS LIKE '%Pennsylvania%'", where_clause)

    @patch('src.entities.dc_project.api.requests.get')
    def test_query_arcgis_exception(self, mock_get):
        """Test _query_arcgis handles exceptions gracefully and breaks loop"""
        # Properly raise the mock Exception instead of returning a MagicMock
        mock_get.side_effect = MockRequestException("API Error")

        features = _query_arcgis("http://fake-url")
        self.assertEqual(features, [])
        self.assertEqual(mock_get.call_count, 1)

    @patch('src.entities.dc_project.api._query_arcgis')
    @patch('src.entities.dc_project.api._fetch_geojson_fallback')
    @patch('src.entities.dc_project.api.pd.DataFrame')
    def test_fetch_dc_data_success(self, mock_df, mock_fallback, mock_query):
        """Test fetch_dc_data returns a dataframe of features when _query_arcgis is successful"""
        mock_query.return_value = [
            {"attributes": {"name": "Project A"}},
            {"attributes": {"name": "Project B"}}
        ]
        mock_df_instance = MagicMock()
        mock_df_instance.shape = (2, 1)
        mock_df.return_value = mock_df_instance

        result = fetch_dc_data(state="DC")

        mock_query.assert_called_once()
        self.assertEqual(mock_query.call_args[1]['state'], "DC")
        mock_fallback.assert_not_called()

        mock_df.assert_called_once_with([{"name": "Project A"}, {"name": "Project B"}])
        self.assertEqual(result, mock_df_instance)

    @patch('src.entities.dc_project.api._query_arcgis')
    @patch('src.entities.dc_project.api._fetch_geojson_fallback')
    def test_fetch_dc_data_fallback(self, mock_fallback, mock_query):
        """Test fetch_dc_data uses fallback when _query_arcgis returns empty"""
        mock_query.return_value = []
        mock_fallback.return_value = "Fallback DataFrame"

        result = fetch_dc_data()

        mock_query.assert_called_once()
        mock_fallback.assert_called_once()
        self.assertEqual(result, "Fallback DataFrame")

    @patch('src.entities.dc_project.api.requests.get')
    @patch('src.entities.dc_project.api.pd.DataFrame')
    def test_fetch_geojson_fallback_success(self, mock_df, mock_get):
        """Test _fetch_geojson_fallback processes geojson correctly"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "features": [
                {
                    "properties": {"name": "Project A"},
                    "geometry": {"coordinates": [-77.0, 38.9]}
                }
            ]
        }
        mock_get.return_value = mock_response

        mock_df_instance = MagicMock()
        mock_df_instance.shape = (1, 3)
        mock_df.return_value = mock_df_instance

        result = _fetch_geojson_fallback()

        mock_get.assert_called_once()

        expected_rows = [
            {"name": "Project A", "LONGITUDE": -77.0, "LATITUDE": 38.9}
        ]
        mock_df.assert_called_once_with(expected_rows)
        self.assertEqual(result, mock_df_instance)

    @patch('src.entities.dc_project.api.requests.get')
    @patch('src.entities.dc_project.api.pd.DataFrame')
    def test_fetch_geojson_fallback_exception(self, mock_df, mock_get):
        """Test _fetch_geojson_fallback handles exceptions and returns empty df"""
        # Properly raise the mock Exception
        mock_get.side_effect = MockRequestException("Fallback API Error")

        mock_df_instance = MagicMock()
        mock_df_instance.shape = (0, 0)
        mock_df.return_value = mock_df_instance

        result = _fetch_geojson_fallback()

        mock_get.assert_called_once()
        self.assertEqual(result, mock_df_instance)

if __name__ == '__main__':
    unittest.main()
