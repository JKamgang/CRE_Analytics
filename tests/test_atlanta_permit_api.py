import sys
import unittest
from unittest.mock import patch, MagicMock

# Now we can import the module to test
from src.entities.atlanta_permit.api import fetch_atlanta_data


class TestAtlantaPermitAPI(unittest.TestCase):

    @patch('src.entities.atlanta_permit.api.requests.get')
    def test_fetch_atlanta_data_sql_injection(self, mock_get):
        # Setup mock to return an empty features list to terminate the loop
        mock_response = MagicMock()
        mock_response.json.return_value = {"features": []}
        mock_get.return_value = mock_response

        # Test with malicious input for state
        malicious_input = "GA' OR 1=1--"
        fetch_atlanta_data(state=malicious_input)

        # Assert that the where clause properly sanitizes the input
        self.assertEqual(mock_get.call_count, 1)

        # Get the first call (the main API call)
        args, kwargs = mock_get.call_args_list[0]
        params = kwargs.get('params')

        # We expect the ' in the input to be replaced by ''
        expected_where_clause = "1=1 AND STATE = 'GA'' OR 1=1--'"
        self.assertEqual(params['where'], expected_where_clause)

    @patch('src.entities.atlanta_permit.api.requests.get')
    def test_fetch_atlanta_data_county_injection(self, mock_get):
        # Setup mock to return an empty features list to terminate the loop
        mock_response = MagicMock()
        mock_response.json.return_value = {"features": []}
        mock_get.return_value = mock_response

        # Test with malicious input for county
        malicious_input = "Fulton%' OR '1'='1"
        fetch_atlanta_data(county=malicious_input)

        # Assert that the where clause properly sanitizes the input
        self.assertEqual(mock_get.call_count, 1)

        # Get the first call (the main API call)
        args, kwargs = mock_get.call_args_list[0]
        params = kwargs.get('params')

        expected_where_clause = "1=1 AND COUNTY LIKE '%Fulton%'' OR ''1''=''1%'"
        self.assertEqual(params['where'], expected_where_clause)


if __name__ == '__main__':
    unittest.main()
