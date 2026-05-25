import unittest
from src.shared.utils.data_processor import generate_sample_data

class TestDataProcessor(unittest.TestCase):
    def test_generate_sample_data_deterministic(self):
        """Test that generate_sample_data returns identical dataframes when called multiple times."""
        df1 = generate_sample_data()
        df2 = generate_sample_data()

        # We use pandas equals to assert the dataframes have exactly identical data and columns
        self.assertTrue(df1.equals(df2), "generate_sample_data should return identical dataframes on subsequent calls.")

if __name__ == '__main__':
    unittest.main()
