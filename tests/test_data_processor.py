import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys

# Mock streamlit cache_data before importing the module to ensure the decorator is mocked at import time
mock_st = MagicMock()
mock_st.cache_data = lambda **kwargs: lambda f: f
sys.modules['streamlit'] = mock_st

from src.shared.utils.data_processor import generate_sample_data

class TestDataProcessor(unittest.TestCase):

    def test_generate_sample_data_predictability(self):
        """Test that generate_sample_data produces deterministic and identical output across calls."""
        # Call the function twice
        df1 = generate_sample_data()
        df2 = generate_sample_data()

        # Verify that 50 rows are returned (2 cities * 25 projects)
        self.assertEqual(len(df1), 50)
        self.assertEqual(len(df2), 50)

        # Verify that both DataFrames are identical
        pd.testing.assert_frame_equal(df1, df2)

if __name__ == '__main__':
    unittest.main()
