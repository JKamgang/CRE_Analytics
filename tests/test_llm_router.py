import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock dependencies to prevent ImportError in the network-restricted environment
sys.modules['dotenv'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()

from src.shared.llm_router import LLMCascadeRouter

class TestLLMCascadeRouter(unittest.TestCase):
    @patch('src.shared.llm_router.Config')
    @patch('src.shared.llm_router.genai')
    def test_primary_gemini_success(self, mock_genai, mock_config):
        mock_config.GEMINI_API_KEY = 'fake_key'

        router = LLMCascadeRouter(use_local_only=False)

        # Configure the mock returned by genai.GenerativeModel
        mock_response = MagicMock()
        mock_response.text = "Gemini Response"
        router.gemini_model.generate_content.return_value = mock_response

        result = router.route_request("Test prompt")

        self.assertEqual(result, "Gemini Response")
        router.gemini_model.generate_content.assert_called_once_with("Test prompt")

    @patch('src.shared.llm_router.Config')
    @patch('src.shared.llm_router.genai')
    def test_cascade_gemini_to_gemma(self, mock_genai, mock_config):
        mock_config.GEMINI_API_KEY = 'fake_key'

        router = LLMCascadeRouter(use_local_only=False)

        # Force Gemini to fail
        router.gemini_model.generate_content.side_effect = Exception("Gemini API Error")

        result = router.route_request("stagnation")

        self.assertIn("[Gemma 4 - Local AI Assistant]", result)
        self.assertIn("High stagnation Z-scores", result)

    @patch('src.shared.llm_router.Config')
    @patch('src.shared.llm_router.genai')
    def test_cascade_gemma_to_llama(self, mock_genai, mock_config):
        mock_config.GEMINI_API_KEY = 'fake_key'

        router = LLMCascadeRouter(use_local_only=False)

        # Force Gemini to fail
        router.gemini_model.generate_content.side_effect = Exception("Gemini API Error")

        # Force Gemma to fail
        with patch.object(router, '_call_local_gemma_4', side_effect=Exception("Gemma Error")):
            result = router.route_request("atlanta")

            self.assertIn("[Llama 3 - Failover Assistant]", result)
            self.assertIn("Atlanta shows strong growth", result)

    def test_local_only_mode(self):
        # When use_local_only=True, it bypasses Gemini init completely
        router = LLMCascadeRouter(use_local_only=True)
        self.assertIsNone(router.gemini_model)

        result = router.route_request("general prompt")

        self.assertIn("[Gemma 4 - Local AI Assistant]", result)
        self.assertIn("I am here to help you interpret CRE Growth Dynamics", result)

if __name__ == '__main__':
    unittest.main()
