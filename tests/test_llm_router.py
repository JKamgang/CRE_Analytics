import unittest
from unittest.mock import patch
from src.shared.llm_router import LLMCascadeRouter
from src.shared.config.settings import Config

class TestLLMCascadeRouter(unittest.TestCase):
    @patch('src.shared.llm_router.genai.configure')
    @patch.object(Config, 'GEMINI_API_KEY', 'dummy_key')
    def test_gemini_api_configuration_failure_handling(self, mock_configure):
        # Arrange
        mock_configure.side_effect = Exception("Mocked configuration error")

        # Act
        router = LLMCascadeRouter(use_local_only=False)

        # Assert
        self.assertIsNone(router.gemini_model)
        mock_configure.assert_called_once_with(api_key="dummy_key")

if __name__ == '__main__':
    unittest.main()
