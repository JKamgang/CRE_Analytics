import unittest
import sys
from unittest.mock import patch, MagicMock

# Mock dependencies as network restricted
sys.modules['requests'] = MagicMock()
sys.modules['pandas'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['streamlit'] = MagicMock()

from src.entities.atlanta_permit.api import _query_arcgis

class TestAtlantaPermitApi(unittest.TestCase):
    @patch('src.entities.atlanta_permit.api.requests.get')
    def test_query_arcgis_sanitizes_injection(self, mock_get):
        # Setup mock to break the loop immediately
        mock_response = MagicMock()
        mock_response.json.return_value = {"features": []}
        mock_get.return_value = mock_response

        # Payload with a potential injection attack
        malicious_payload = "GA' OR '1'='1"

        _query_arcgis(
            base_url="http://fake-url",
            state=malicious_payload,
            county=malicious_payload,
            zip_code=malicious_payload,
            street=malicious_payload
        )

        mock_get.assert_called()

        call_kwargs = mock_get.call_args.kwargs
        params = call_kwargs.get("params", {})
        where_clause = params.get("where", "")

        expected_sanitized = "GA'' OR ''1''=''1"

        self.assertIn(f"STATE = '{expected_sanitized}'", where_clause)
        self.assertIn(f"COUNTY LIKE '%{expected_sanitized}%'", where_clause)
        self.assertIn(f"ZIPCODE = '{expected_sanitized}'", where_clause)
        self.assertIn(f"ADDRESS LIKE '%{expected_sanitized}%'", where_clause)

if __name__ == '__main__':
    unittest.main()
