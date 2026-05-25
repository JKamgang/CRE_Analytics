import sys
from unittest.mock import MagicMock

# Mock required missing libraries before imports
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['dotenv'] = MagicMock()

import unittest
from unittest.mock import patch
import os

# Add src to path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.shared.llm_router import LLMCascadeRouter

class TestLLMRouter(unittest.TestCase):
    @patch('src.shared.llm_router.genai')
    @patch('src.shared.llm_router.Config')
    def test_gemini_initialization_failure(self, mock_config, mock_genai):
        # Configure mock_config
        mock_config.GEMINI_API_KEY = 'test_key'

        # Configure mock_genai to raise exception on configure
        mock_genai.configure.side_effect = Exception("API connection error")

        # Initialize router
        router = LLMCascadeRouter(use_local_only=False)

        # Verify gemini_model is gracefully set to None
        self.assertIsNone(router.gemini_model)

        # Verify configure was called with expected api_key
        mock_genai.configure.assert_called_once_with(api_key='test_key')

if __name__ == '__main__':
    unittest.main()
