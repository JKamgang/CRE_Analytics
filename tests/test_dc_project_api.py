import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.entities.dc_project.api import _query_arcgis, fetch_dc_data, _fetch_geojson_fallback

class TestDCProjectAPI(unittest.TestCase):
    @patch('src.entities.dc_project.api.requests.get')
    def test_query_arcgis_pagination(self, mock_get):
        # Set up mock to return two pages of results
        mock_response_1 = MagicMock()
        mock_response_1.json.return_value = {
            "features": [{"attributes": {"id": 1}}, {"attributes": {"id": 2}}]
        }

        mock_response_2 = MagicMock()
        mock_response_2.json.return_value = {
            "features": [{"attributes": {"id": 3}}]
        }

        mock_get.side_effect = [mock_response_1, mock_response_2]

        # Call with max_records=2 so the first page is exactly max_records, triggering a second page fetch
        features = _query_arcgis("http://fake-url", max_records=2)

        self.assertEqual(len(features), 3)
        self.assertEqual(mock_get.call_count, 2)

        # Verify first call
        first_call_args = mock_get.call_args_list[0][1]['params']
        self.assertEqual(first_call_args['resultOffset'], 0)
        self.assertEqual(first_call_args['resultRecordCount'], 2)

        # Verify second call
        second_call_args = mock_get.call_args_list[1][1]['params']
        self.assertEqual(second_call_args['resultOffset'], 2)

    @patch('src.entities.dc_project.api._query_arcgis')
    def test_fetch_dc_data_success(self, mock_query):
        # Setup mock to return some features
        mock_query.return_value = [
            {"attributes": {"PROJECTNAME": "Test Project 1", "ESTVALUEINMILLION": 10}},
            {"attributes": {"PROJECTNAME": "Test Project 2", "ESTVALUEINMILLION": 20}}
        ]

        df = fetch_dc_data()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn("PROJECTNAME", df.columns)
        self.assertEqual(df["PROJECTNAME"].iloc[0], "Test Project 1")

    @patch('src.entities.dc_project.api._fetch_geojson_fallback')
    @patch('src.entities.dc_project.api._query_arcgis')
    def test_fetch_dc_data_fallback(self, mock_query, mock_fallback):
        # Return empty list to trigger fallback
        mock_query.return_value = []

        # Setup fallback mock
        expected_df = pd.DataFrame({"PROJECTNAME": ["Fallback Project"]})
        mock_fallback.return_value = expected_df

        df = fetch_dc_data()

        mock_fallback.assert_called_once()
        self.assertEqual(len(df), 1)
        self.assertEqual(df["PROJECTNAME"].iloc[0], "Fallback Project")

    @patch('src.entities.dc_project.api.requests.get')
    def test_fetch_geojson_fallback(self, mock_get):
        # Setup mock to return a valid GeoJSON
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "features": [
                {
                    "properties": {"PROJECTNAME": "GeoJSON Project"},
                    "geometry": {"coordinates": [-77.0, 38.9]}
                }
            ]
        }
        mock_get.return_value = mock_response

        df = _fetch_geojson_fallback()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        self.assertEqual(df["PROJECTNAME"].iloc[0], "GeoJSON Project")
        self.assertEqual(df["LONGITUDE"].iloc[0], -77.0)
        self.assertEqual(df["LATITUDE"].iloc[0], 38.9)

if __name__ == '__main__':
    unittest.main()
