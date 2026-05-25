import sys
from unittest.mock import MagicMock
sys.modules['pandas'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['streamlit'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['google.genai'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['pydantic'] = MagicMock()

import unittest
if __name__ == '__main__':
    unittest.TextTestRunner().run(unittest.TestLoader().discover('tests'))
