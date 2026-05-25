import unittest
from unittest.mock import patch, MagicMock
from src.shared.llm_router import LLMCascadeRouter

class TestLLMCascadeRouter(unittest.TestCase):

    def setUp(self):
        # We patch Config so that we can pretend GEMINI_API_KEY exists if we want it to.
        # But we mostly test the cascade logic which doesn't strictly depend on the real Config.
        pass

    @patch('src.shared.llm_router.Config')
    def test_route_request_gemini_success(self, mock_config):
        """Test that if gemini_model succeeds, it returns the generated response."""
        # Setup mock router
        mock_config.GEMINI_API_KEY = "test_key"

        # We need to manually set gemini_model because init might fail if the mock isn't right
        router = LLMCascadeRouter(use_local_only=False)
        router.gemini_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Gemini Response"
        router.gemini_model.generate_content.return_value = mock_response

        # We spy on local fallback to ensure it's NOT called
        with patch.object(router, '_call_local_gemma_4') as mock_gemma:
            response = router.route_request("Hello")

            self.assertEqual(response, "Gemini Response")
            router.gemini_model.generate_content.assert_called_once_with("Hello")
            mock_gemma.assert_not_called()

    @patch('src.shared.llm_router.Config')
    def test_route_request_gemini_fail_cascade_to_gemma_success(self, mock_config):
        """Test that if gemini_model.generate_content throws an exception, it cascades to _call_local_gemma_4."""
        mock_config.GEMINI_API_KEY = "test_key"

        router = LLMCascadeRouter(use_local_only=False)
        router.gemini_model = MagicMock()
        # Make Gemini fail
        router.gemini_model.generate_content.side_effect = Exception("Gemini API Error")

        with patch.object(router, '_call_local_gemma_4', return_value="Gemma Response") as mock_gemma:
            with patch.object(router, '_call_local_llama_3') as mock_llama:
                response = router.route_request("Hello")

                self.assertEqual(response, "Gemma Response")
                router.gemini_model.generate_content.assert_called_once_with("Hello")
                mock_gemma.assert_called_once_with("Hello")
                mock_llama.assert_not_called()

    @patch('src.shared.llm_router.Config')
    def test_route_request_gemma_fail_cascade_to_llama(self, mock_config):
        """Test that if _call_local_gemma_4 also raises an exception, the router cascades down to _call_local_llama_3."""
        mock_config.GEMINI_API_KEY = "test_key"

        router = LLMCascadeRouter(use_local_only=False)
        router.gemini_model = MagicMock()
        # Make Gemini fail
        router.gemini_model.generate_content.side_effect = Exception("Gemini API Error")

        # Make Gemma fail
        with patch.object(router, '_call_local_gemma_4', side_effect=Exception("Gemma Error")) as mock_gemma:
            with patch.object(router, '_call_local_llama_3', return_value="Llama Response") as mock_llama:
                response = router.route_request("Hello")

                self.assertEqual(response, "Llama Response")
                router.gemini_model.generate_content.assert_called_once_with("Hello")
                mock_gemma.assert_called_once_with("Hello")
                mock_llama.assert_called_once_with("Hello")

    def test_route_request_use_local_only(self):
        """Test that if use_local_only=True, the router skips gemini_model entirely."""
        router = LLMCascadeRouter(use_local_only=True)
        # Even if gemini_model is populated, it shouldn't be used
        router.gemini_model = MagicMock()

        with patch.object(router, '_call_local_gemma_4', return_value="Gemma Response") as mock_gemma:
            response = router.route_request("Hello")

            self.assertEqual(response, "Gemma Response")
            router.gemini_model.generate_content.assert_not_called()
            mock_gemma.assert_called_once_with("Hello")

if __name__ == '__main__':
    unittest.main()
