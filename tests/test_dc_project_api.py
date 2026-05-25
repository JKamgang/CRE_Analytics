import unittest
from unittest.mock import patch, MagicMock

import pandas as pd
import requests
from src.entities.dc_project.api import (
    _query_arcgis,
    fetch_dc_data,
    _fetch_geojson_fallback,
    normalize_dc_data,
    save_dc_data,
    run_dc_pipeline
)
from src.shared.config.settings import DC_CONFIG

class TestDCProjectAPI(unittest.TestCase):
    @patch('src.entities.dc_project.api.requests.get')
    def test_query_arcgis_success(self, mock_get):
        # Setup mock to return a page of features then an empty page
        mock_resp_1 = MagicMock()
        mock_resp_1.json.return_value = {"features": [{"attributes": {"id": 1}}, {"attributes": {"id": 2}}]}
        mock_resp_2 = MagicMock()
        mock_resp_2.json.return_value = {"features": []}
        mock_get.side_effect = [mock_resp_1, mock_resp_2]

        features = _query_arcgis("http://fake-url", max_records=2)

        self.assertEqual(len(features), 2)
        self.assertEqual(mock_get.call_count, 2)
        # Check that offset was incremented
        args1, kwargs1 = mock_get.call_args_list[0]
        self.assertEqual(kwargs1['params']['resultOffset'], 0)

        # We test that where clauses are combined with AND
        self.assertEqual(kwargs1['params']['where'], "1=1")

        args2, kwargs2 = mock_get.call_args_list[1]
        self.assertEqual(kwargs2['params']['resultOffset'], 2)

    @patch('src.entities.dc_project.api.requests.get')
    def test_query_arcgis_where_clauses(self, mock_get):
        mock_resp_1 = MagicMock()
        mock_resp_1.json.return_value = {"features": [{"attributes": {"id": 1}}]}
        mock_get.side_effect = [mock_resp_1] # Returns 1 feature, < max_records (2000), so breaks loop

        _query_arcgis("http://fake-url", state="DC", county="Washington", zip_code="20001", street="Main")

        args, kwargs = mock_get.call_args
        where_clause = kwargs['params']['where']

        self.assertIn("1=1", where_clause)
        self.assertIn("STATE = 'DC'", where_clause)
        self.assertIn("COUNTY LIKE '%Washington%'", where_clause)
        self.assertIn("ZIPCODE = '20001'", where_clause)
        self.assertIn("ADDRESS LIKE '%Main%'", where_clause)

    @patch('src.entities.dc_project.api.requests.get')
    def test_query_arcgis_request_exception(self, mock_get):
        mock_get.side_effect = requests.RequestException("API error")
        features = _query_arcgis("http://fake-url")
        self.assertEqual(len(features), 0)

    @patch('src.entities.dc_project.api._query_arcgis')
    def test_fetch_dc_data_success(self, mock_query):
        mock_query.return_value = [{"attributes": {"A": 1}}, {"attributes": {"A": 2}}]

        result = fetch_dc_data(state="DC")

        mock_query.assert_called_once_with(DC_CONFIG["arcgis_feature_server"], DC_CONFIG["max_record_count"], state="DC")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape, (2, 1))
        self.assertEqual(result.iloc[0]['A'], 1)

    @patch('src.entities.dc_project.api._query_arcgis')
    @patch('src.entities.dc_project.api._fetch_geojson_fallback')
    def test_fetch_dc_data_fallback(self, mock_fallback, mock_query):
        mock_query.return_value = []
        mock_fallback.return_value = pd.DataFrame({"B": [1, 2]})

        result = fetch_dc_data()

        mock_fallback.assert_called_once()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape, (2, 1))
        self.assertEqual(result.iloc[0]['B'], 1)

    @patch('src.entities.dc_project.api.requests.get')
    def test_fetch_geojson_fallback_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "features": [
                {"properties": {"A": 1}, "geometry": {"coordinates": [-77.0, 38.0]}}
            ]
        }
        mock_get.return_value = mock_resp

        result = _fetch_geojson_fallback()

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape, (1, 3))
        self.assertEqual(result.iloc[0]['A'], 1)
        self.assertEqual(result.iloc[0]['LONGITUDE'], -77.0)
        self.assertEqual(result.iloc[0]['LATITUDE'], 38.0)

    @patch('src.entities.dc_project.api.requests.get')
    def test_fetch_geojson_fallback_exception(self, mock_get):
        mock_get.side_effect = requests.RequestException("Fallback error")

        result = _fetch_geojson_fallback()

        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)

    def test_normalize_dc_data_empty(self):
        df = pd.DataFrame()
        result = normalize_dc_data(df)
        self.assertTrue(result.empty)

    def test_normalize_dc_data_mapping(self):
        raw_df = pd.DataFrame([
            {
                "PROJECTNAME": "Test Project 1",
                "WARD": "Ward 1",
                "ADDRESS": "123 Test St",
                "DEVELOPER": "Test Dev",
                "ARCHITECT": "Test Arch",
                "PROJECTTYPE": "apartment",
                "STATUS": "Under Construction",
                "SQFT": 10000,
                "UNITS": 100,
                "ESTVALUEINMILLION": 50,
                "ESTDELIVERY": "Q4 2025",
                "REPORT_EDITION_YEAR": "2024-2025",
                "LATITUDE": 38.0,
                "LONGITUDE": -77.0
            }
        ])

        result = normalize_dc_data(raw_df)

        self.assertFalse(result.empty)
        self.assertEqual(result.iloc[0]["project_name"], "Test Project 1")
        self.assertEqual(result.iloc[0]["city"], "DC")
        self.assertEqual(result.iloc[0]["ward"], "Ward 1")
        self.assertEqual(result.iloc[0]["neighborhood"], "123 Test St")
        self.assertEqual(result.iloc[0]["developer"], "Test Dev")
        self.assertEqual(result.iloc[0]["architect"], "Test Arch")
        self.assertEqual(result.iloc[0]["sector"], "Multifamily")
        self.assertEqual(result.iloc[0]["status"], "Under Construction")
        self.assertEqual(result.iloc[0]["sqft"], 10000)
        self.assertEqual(result.iloc[0]["units"], 100)
        self.assertEqual(result.iloc[0]["est_value_millions"], 50)
        self.assertEqual(result.iloc[0]["est_delivery"], "Q4 2025")
        self.assertEqual(result.iloc[0]["report_year"], 2025)
        self.assertEqual(result.iloc[0]["latitude"], 38.0)
        self.assertEqual(result.iloc[0]["longitude"], -77.0)

    @patch('src.entities.dc_project.api.os.makedirs')
    @patch('src.entities.dc_project.api.os.path.join')
    @patch('src.entities.dc_project.api.pd.DataFrame.to_csv')
    def test_save_dc_data(self, mock_to_csv, mock_join, mock_makedirs):
        mock_join.side_effect = lambda a, b: f"{a}/{b}"

        raw_df = pd.DataFrame([{"A": 1}])
        processed_df = pd.DataFrame([{"B": 1}])

        raw_path, proc_path = save_dc_data(raw_df, processed_df)

        self.assertEqual(mock_makedirs.call_count, 2)
        self.assertEqual(mock_to_csv.call_count, 2)
        self.assertTrue(raw_path.endswith(DC_CONFIG["raw_file"]))
        self.assertTrue(proc_path.endswith(DC_CONFIG["processed_file"]))

    @patch('src.entities.dc_project.api.fetch_dc_data')
    @patch('src.entities.dc_project.api.normalize_dc_data')
    @patch('src.entities.dc_project.api.save_dc_data')
    def test_run_dc_pipeline(self, mock_save, mock_normalize, mock_fetch):
        mock_raw = pd.DataFrame([{"A": 1}])
        mock_fetch.return_value = mock_raw

        mock_processed = pd.DataFrame([{"B": 1}])
        mock_normalize.return_value = mock_processed

        result = run_dc_pipeline(state="DC")

        mock_fetch.assert_called_once_with(state="DC")
        mock_normalize.assert_called_once_with(mock_raw)
        mock_save.assert_called_once_with(mock_raw, mock_processed)
        self.assertTrue(result.equals(mock_processed))

    @patch('src.entities.dc_project.api.fetch_dc_data')
    @patch('src.entities.dc_project.api.normalize_dc_data')
    @patch('src.entities.dc_project.api.save_dc_data')
    def test_run_dc_pipeline_empty(self, mock_save, mock_normalize, mock_fetch):
        mock_raw = pd.DataFrame()
        mock_fetch.return_value = mock_raw

        mock_processed = pd.DataFrame()
        mock_normalize.return_value = mock_processed

        result = run_dc_pipeline()

        mock_fetch.assert_called_once()
        mock_normalize.assert_called_once_with(mock_raw)
        mock_save.assert_not_called()
        self.assertTrue(result.empty)

if __name__ == '__main__':
    unittest.main()
