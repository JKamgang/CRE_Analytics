import unittest
import sys
import os
from unittest.mock import MagicMock

sys.modules['dotenv'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['google.genai'] = MagicMock()

st_mock = MagicMock()
st_mock.cache_data = lambda **kwargs: lambda f: f
sys.modules['streamlit'] = st_mock

# Ensure src path is correctly configured
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.shared.utils.data_processor import generate_sample_data

class TestDataProcessor(unittest.TestCase):
    def test_generate_sample_data_determinism(self):
        """Test that sample data generation is completely deterministic"""
        # Call it first time
        df1 = generate_sample_data()

        # Call it second time
        df2 = generate_sample_data()

        # Verify the two DataFrames are identical
        self.assertTrue(df1.equals(df2), "Sample data generation is not deterministic; consecutive calls produced different data.")

        # Validate expected shape
        # (2 cities * 25 rows = 50 rows)
        self.assertEqual(len(df1), 50)

        # Validate columns exist in the generated rows
        required_keys = ["project_name", "city", "ward", "sector", "status", "sqft", "est_value_millions", "report_year", "latitude", "longitude"]
        for key in required_keys:
            self.assertIn(key, df1.columns)

if __name__ == '__main__':
    unittest.main()
