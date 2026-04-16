import unittest
import pandas as pd
import numpy as np
from src.features.growth_status.calculator import GrowthStatusCalculator

class TestGrowthStatusCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = GrowthStatusCalculator()

    def test_calculate_growth_metrics_empty(self):
        df = pd.DataFrame()
        result = self.calculator.calculate_growth_metrics(df)
        self.assertTrue(result.empty)

    def test_calculate_growth_metrics_no_target_col(self):
        df = pd.DataFrame({'other_col': [1, 2, 3]})
        result = self.calculator.calculate_growth_metrics(df)
        self.assertNotIn('z_score', result.columns)
        self.assertNotIn('growth_status', result.columns)

    def test_calculate_growth_metrics_est_value_millions(self):
        df = pd.DataFrame({'est_value_millions': [5, 10, 15]})
        result = self.calculator.calculate_growth_metrics(df.copy())

        self.assertIn('z_score', result.columns)
        self.assertIn('growth_status', result.columns)

        self.assertAlmostEqual(result['z_score'].iloc[0], -1.0)
        self.assertAlmostEqual(result['z_score'].iloc[1], 0.0)
        self.assertAlmostEqual(result['z_score'].iloc[2], 1.0)

        self.assertEqual(result['growth_status'].iloc[0], 'Stagnation')
        self.assertEqual(result['growth_status'].iloc[1], 'Stagnation')
        self.assertEqual(result['growth_status'].iloc[2], 'Stagnation')

    def test_calculate_growth_metrics_categories(self):
        df = pd.DataFrame({'sqft': [0, 50, 100, 100, 100, 250]})
        result = self.calculator.calculate_growth_metrics(df)

        self.assertEqual(result['growth_status'].iloc[0], 'Decline')     # z < -1
        self.assertEqual(result['growth_status'].iloc[2], 'Stagnation')  # -1 <= z <= 1
        self.assertEqual(result['growth_status'].iloc[5], 'Increase')    # z > 1

    def test_calculate_growth_metrics_zero_std(self):
        df = pd.DataFrame({'sqft': [10, 10, 10]})
        result = self.calculator.calculate_growth_metrics(df)

        self.assertEqual(result['z_score'].iloc[0], 0.0)
        self.assertEqual(result['growth_status'].iloc[0], 'Stagnation')

    def test_calculate_growth_metrics_with_nans(self):
        df = pd.DataFrame({'est_value_millions': [5, np.nan, 15]})
        result = self.calculator.calculate_growth_metrics(df)

        self.assertIn('z_score', result.columns)
        self.assertIn('growth_status', result.columns)

    def test_get_status_summary(self):
        df = pd.DataFrame({'growth_status': ['Increase', 'Stagnation', 'Increase', 'Decline']})
        summary = self.calculator.get_status_summary(df)

        expected = {'Increase': 2, 'Stagnation': 1, 'Decline': 1}
        self.assertEqual(summary, expected)

    def test_get_status_summary_no_col(self):
        df = pd.DataFrame({'other_col': [1, 2, 3]})
        summary = self.calculator.get_status_summary(df)

        self.assertEqual(summary, {})

if __name__ == '__main__':
    unittest.main()
