import sys
from unittest.mock import MagicMock

# Mock required dependencies
sys.modules['pandas'] = MagicMock()
sys.modules['streamlit'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['google.genai'] = MagicMock()

import unittest
if __name__ == '__main__':
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    sys.exit(not result.wasSuccessful())
