import sys
from unittest.mock import MagicMock

# Mock necessary external dependencies for tests to run in restricted environment
sys.modules['pandas'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['google.genai'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['streamlit'] = MagicMock()
sys.modules['numpy'] = MagicMock()
