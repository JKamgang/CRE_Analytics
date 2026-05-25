import unittest
from unittest.mock import patch, MagicMock

import sys
import os

# Ensure src is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.entities.dc_project.api import _query_arcgis

class TestDCApiSecurity(unittest.TestCase):
    @patch('src.entities.dc_project.api.requests.get')
    def test_query_injection_sanitization(self, mock_get):
        # Mock the response so it breaks the while True loop gracefully
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"features": []}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        # Pass inputs with single quotes to simulate injection attempt
        malicious_state = "DC' OR 1=1 --"
        malicious_county = "Washington'--"
        malicious_zip = "20001' OR 'a'='a"
        malicious_street = "Main St'; DROP TABLE USERS;--"

        _query_arcgis(
            base_url="http://fake-url",
            state=malicious_state,
            county=malicious_county,
            zip_code=malicious_zip,
            street=malicious_street
        )

        # Check what arguments requests.get was called with
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        params = kwargs.get('params', {})
        where_clause = params.get('where', '')

        # Ensure that all single quotes in user input have been replaced with double single quotes ('')
        expected_state = malicious_state.replace("'", "''")
        expected_county = malicious_county.replace("'", "''")
        expected_zip = malicious_zip.replace("'", "''")
        expected_street = malicious_street.replace("'", "''")

        self.assertIn(f"STATE = '{expected_state}'", where_clause)
        self.assertIn(f"COUNTY LIKE '%{expected_county}%'", where_clause)
        self.assertIn(f"ZIPCODE = '{expected_zip}'", where_clause)
        self.assertIn(f"ADDRESS LIKE '%{expected_street}%'", where_clause)

if __name__ == '__main__':
    unittest.main()
