import sys
from unittest.mock import MagicMock

# Removing mocks for pandas and numpy since we installed them
# sys.modules['requests'] = MagicMock() - Keeping this only where needed or not mocking it globally, actually test_ga_metro_api already mocks it in the file. But test_tracker might need streamlit and dotenv. Let's provide them here.
sys.modules['streamlit'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['google.genai'] = MagicMock()

import unittest
if __name__ == '__main__':
    unittest.main(module=None, argv=['', 'discover', 'tests'])
