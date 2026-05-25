import sys
from unittest.mock import MagicMock

sys.modules['dotenv'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['google.genai'] = MagicMock()

st_mock = MagicMock()
st_mock.cache_data = lambda **kwargs: lambda f: f
sys.modules['streamlit'] = st_mock
