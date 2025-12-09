
import unittest
from unittest.mock import MagicMock, patch
from src.agents.providers.factory import LLMProviderFactory
from src.config import LLMDICT

class TestLLMProviderFactory(unittest.TestCase):
    def setUp(self):
        # Ensure at least one provider is in LLMDICT for testing
        if "MOCK_PROVIDER" not in LLMDICT:
             # We can't easily modify LLMDICT if it's imported, so we rely on existing keys or patch it
             pass

    @patch("src.agents.providers.factory.get_azure_client")
    def test_create_azure_client(self, mock_get_client):
        # Mock the client creation
        mock_client = MagicMock()
        mock_client.deployment_name = "mock-model"
        mock_get_client.return_value = mock_client
        
        # Test creation
        # Assumption: AZURE is in LLMDICT or will be passed if we patch LLMDICT
        with patch.dict("src.agents.providers.factory.LLMDICT", {"AZURE": "key"}, clear=False):
            client = LLMProviderFactory.create("AZURE", agent_name="TestAgent")
            
        self.assertIsNotNone(client)
        self.assertEqual(client, mock_client)
        mock_get_client.assert_called_once()

    @patch("src.agents.providers.factory.get_claude_client")
    def test_create_claude_client(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        with patch.dict("src.agents.providers.factory.LLMDICT", {"OPSUS": "key"}, clear=False):
            client = LLMProviderFactory.create("OPSUS", agent_name="TestAgent")
            
        self.assertIsNotNone(client)
        self.assertEqual(client, mock_client)
        mock_get_client.assert_called_once()

    def test_unknown_provider(self):
        with patch.dict("src.agents.providers.factory.LLMDICT", {}, clear=True):
             client = LLMProviderFactory.create("UNKNOWN_PROVIDER")
        self.assertIsNone(client)

if __name__ == '__main__':
    unittest.main()
