import sys
import unittest.mock

sys.modules['requests'] = unittest.mock.MagicMock()
sys.modules['pandas'] = unittest.mock.MagicMock()

import unittest
from unittest.mock import patch
from src.entities.md_permit.api import fetch_maryland_permits

class TestMDPermitAPI(unittest.TestCase):

    @patch('src.entities.md_permit.api.requests.get')
    def test_fetch_maryland_permits_sql_injection(self, mock_get):
        # Setup mock
        mock_get.return_value.json.return_value = {}

        # Malicious input
        malicious_input = "MD' OR 1=1--"
        fetch_maryland_permits(state=malicious_input)

        # Assert where clause properly sanitizes the input
        self.assertEqual(mock_get.call_count, 1)
        args, kwargs = mock_get.call_args_list[0]
        params = kwargs.get('params')

        expected_where_clause = "1=1 AND STATE = 'MD'' OR 1=1--'"
        self.assertEqual(params['where'], expected_where_clause)

    @patch('src.entities.md_permit.api.requests.get')
    def test_fetch_maryland_permits_county_injection(self, mock_get):
        # Setup mock
        mock_get.return_value.json.return_value = {}

        malicious_input = "Montgomery%' OR '1'='1"
        fetch_maryland_permits(county=malicious_input)

        self.assertEqual(mock_get.call_count, 1)
        args, kwargs = mock_get.call_args_list[0]
        params = kwargs.get('params')

        expected_where_clause = "1=1 AND COUNTY LIKE '%Montgomery%'' OR ''1''=''1%'"
        self.assertEqual(params['where'], expected_where_clause)

if __name__ == '__main__':
    unittest.main()
