import unittest
from unittest.mock import patch

from src.entities.ga_metro.api import fetch_atlanta_metro_regional_data

class TestGAMetroAPI(unittest.TestCase):

    @patch('src.entities.ga_metro.api.requests.get')
    def test_fetch_atlanta_metro_regional_data_sql_injection(self, mock_get):
        # Setup mock to return an empty JSON response so it doesn't crash on dataframe parsing
        mock_get.return_value.json.return_value = {}

        # Test with malicious input
        malicious_input = "GA' OR 1=1--"
        fetch_atlanta_metro_regional_data(state=malicious_input)

        # Assert that the where clause properly sanitizes the input
        # It's called twice because of the fallback mechanism
        self.assertEqual(mock_get.call_count, 2)

        # Get the first call (the main API call)
        args, kwargs = mock_get.call_args_list[0]
        params = kwargs.get('params')

        # We expect the ' in the input to be replaced by ''
        expected_where_clause = "1=1 AND STATE_ABBR = 'GA'' OR 1=1--'"
        self.assertEqual(params['where'], expected_where_clause)

    @patch('src.entities.ga_metro.api.requests.get')
    def test_fetch_atlanta_metro_regional_data_county_injection(self, mock_get):
        # Setup mock to return an empty JSON response
        mock_get.return_value.json.return_value = {}

        # Test with malicious input
        malicious_input = "Fulton%' OR '1'='1"
        fetch_atlanta_metro_regional_data(county=malicious_input)

        # Assert that the where clause properly sanitizes the input
        # It's called twice because of the fallback mechanism
        self.assertEqual(mock_get.call_count, 2)

        # Get the first call (the main API call)
        args, kwargs = mock_get.call_args_list[0]
        params = kwargs.get('params')

        expected_where_clause = "1=1 AND COUNTY LIKE '%Fulton%'' OR ''1''=''1%'"
        self.assertEqual(params['where'], expected_where_clause)

if __name__ == '__main__':
    unittest.main()
