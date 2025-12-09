
import unittest
from unittest.mock import MagicMock, patch
from src.agents.llm_agent import LLMAgent
from src.agents.base_agent import Action, ActionType, Observation, Message
from src.agents.tools.registry import ToolRegistry

class TestLLMAgentRefactor(unittest.TestCase):
    def setUp(self):
        self.agent = LLMAgent("test_agent", "Test AI", llm_provider="MOCK")
        # Mock LLM client
        self.agent.llm = MagicMock()
        self.agent.llm.deployment_name = "mock-gpt-4" # Simulate Azure client behavior
        
        # Mock Observation
        self.obs = Observation(
            week=1,
            season="Spring",
            my_stats={"balance": 1000, "inventory": {"soap": 50}, "price": 5.0, "reputation": 50, "machines": 4},
            competitor_stats=[],
            messages=[],
            events=[],
            market_data={}
        )

    def test_decide_action_returns_list(self):
        # Mock LLM response to return a single tool call then end_turn
        
        # Response 1: set_price
        mock_response_1 = MagicMock()
        mock_message_1 = MagicMock()
        mock_message_1.content = "Thinking about price..."
        
        tool_call_1 = MagicMock()
        tool_call_1.function.name = "set_price"
        tool_call_1.function.arguments = '{"price": 4.50}'
        tool_call_1.id = "call_1"
        
        mock_message_1.tool_calls = [tool_call_1]
        mock_response_1.choices = [MagicMock(message=mock_message_1)]
        
        # Response 2: end_turn
        mock_response_2 = MagicMock()
        mock_message_2 = MagicMock()
        mock_message_2.content = "Done."
        
        tool_call_2 = MagicMock()
        tool_call_2.function.name = "end_turn"
        tool_call_2.function.arguments = '{"memory_note": "Lowered price."}'
        tool_call_2.id = "call_2"
        
        mock_message_2.tool_calls = [tool_call_2]
        mock_response_2.choices = [MagicMock(message=mock_message_2)]
        
        # Setup side effects for the loop
        self.agent._call_llm_messages = MagicMock(side_effect=[mock_response_1, mock_response_2])
        
        # Override _parse_single_tool slightly to ensure it works without complex imports if needed
        # But real method should work if imports are fine.
        
        actions = self.agent.decide_action(self.obs)
        
        self.assertIsInstance(actions, list)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].type, ActionType.SET_PRICE)
        self.assertEqual(actions[0].parameters["price"], 4.50)
        
        # Verify loop called LLM twice
        self.assertEqual(self.agent._call_llm_messages.call_count, 2)
        
        print(f"Captured Actions: {actions}")

    def test_memory_persistence(self):
        """Test that memory is updated after end_turn and persists to next turn"""
        self.agent.memory = "Initial memory"
        
        # Mock response for turn 1: end_turn with new memory
        mock_response = MagicMock()
        mock_message = MagicMock()
        tool_call = MagicMock()
        tool_call.function.name = "end_turn"
        tool_call.function.arguments = '{"memory_note": "New strategy: raise prices"}'
        tool_call.id = "call_mem"
        
        mock_message.tool_calls = [tool_call]
        mock_response.choices = [MagicMock(message=mock_message)]
        
        self.agent._call_llm_messages = MagicMock(return_value=mock_response)
        
        # Execute turn 1
        self.agent.decide_action(self.obs)
        
        # Verify memory updated
        self.assertEqual(self.agent.memory, "New strategy: raise prices")


if __name__ == '__main__':
    unittest.main()
