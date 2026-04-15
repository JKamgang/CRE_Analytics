import unittest
import sys
import os

# Add src to path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.features.cumulative_flood.tracker import CumulativeFloodTracker

class TestCumulativeFloodTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = CumulativeFloodTracker()

    def test_generate_timeline_default(self):
        """Test default parameters generate a timeline from 2010 to 2026"""
        timeline = self.tracker.generate_timeline()

        # Check timeline length (2010 to 2026 inclusive = 17 years)
        self.assertEqual(len(timeline), 17)

        # Check keys
        for entry in timeline:
            self.assertIn("year", entry)
            self.assertIn("cumulative_flood_level", entry)

        # Check first and last year
        self.assertEqual(timeline[0]["year"], 2010)
        self.assertEqual(timeline[-1]["year"], 2026)

    def test_generate_timeline_custom_years(self):
        """Test custom start and end years"""
        timeline = self.tracker.generate_timeline(start_year=2020, end_year=2025)

        self.assertEqual(len(timeline), 6)
        self.assertEqual(timeline[0]["year"], 2020)
        self.assertEqual(timeline[-1]["year"], 2025)

    def test_generate_timeline_single_year(self):
        """Test single year timeline generation"""
        timeline = self.tracker.generate_timeline(start_year=2022, end_year=2022, base_pressure=10.0)

        self.assertEqual(len(timeline), 1)
        self.assertEqual(timeline[0]["year"], 2022)

        # Base logic:
        # year = 2022
        # current = 10.0
        # growth_factor = 1.05 + (10.0 * 0.01) = 1.15
        # current *= 1.15 -> 11.5
        # variance = (2022 % 3) * 0.5 = 0 * 0.5 = 0.0
        # current += 0.0 -> 11.5
        # round(11.5, 2) = 11.5
        self.assertEqual(timeline[0]["cumulative_flood_level"], 11.5)

    def test_generate_timeline_math_verification(self):
        """Test math calculation for multiple years"""
        # Test case starting in 2020 with base 5.0
        timeline = self.tracker.generate_timeline(start_year=2020, end_year=2022, base_pressure=5.0)

        # Year 2020
        # base: 5.0
        # growth_factor = 1.05 + (5.0 * 0.01) = 1.10
        # new_current = 5.0 * 1.10 = 5.5
        # var = (2020 % 3) * 0.5 = 1 * 0.5 = 0.5
        # total_2020 = 5.5 + 0.5 = 6.0
        self.assertEqual(timeline[0]["cumulative_flood_level"], 6.0)

        # Year 2021
        # current: 6.0
        # growth_factor = 1.05 + (6.0 * 0.01) = 1.11
        # new_current = 6.0 * 1.11 = 6.66
        # var = (2021 % 3) * 0.5 = 2 * 0.5 = 1.0
        # total_2021 = 6.66 + 1.0 = 7.66
        self.assertEqual(timeline[1]["cumulative_flood_level"], 7.66)

        # Year 2022
        # current: 7.66
        # growth_factor = 1.05 + (7.66 * 0.01) = 1.1266
        # new_current = 7.66 * 1.1266 = 8.629756
        # var = (2022 % 3) * 0.5 = 0 * 0.5 = 0.0
        # total_2022 = 8.629756 + 0 = 8.629756 -> round: 8.63
        self.assertEqual(timeline[2]["cumulative_flood_level"], 8.63)

if __name__ == '__main__':
    unittest.main()
