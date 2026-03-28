
import unittest
import json
import os
import time
from agent_core import SimpleAgent

# Mock LLM to avoid API calls
class MockOpenRouterLLM:
    def __init__(self):
        self.api_key = "dummy"
        self.url = "dummy"
        self.model = "dummy"

    def think(self, task, memory):
        return {
            "thought": "Mock thought",
            "action": "execute_command",
            "command": "echo mock_execution"
        }

    def reflect(self, task, plan, result):
        return {
            "success": True,
            "error_analysis": "None",
            "lesson": "Mock lesson works!",
            "confidence": 1.0
        }

class TestAgentReflection(unittest.TestCase):
    def setUp(self):
        # Backup memory if exists
        if os.path.exists("memory.json"):
            os.rename("memory.json", "memory.json.bak")
        
    def tearDown(self):
        # Restore memory
        if os.path.exists("memory.json.bak"):
            if os.path.exists("memory.json"):
                os.remove("memory.json")
            os.rename("memory.json.bak", "memory.json")

    def test_reflection_save(self):
        agent = SimpleAgent()
        agent.llm = MockOpenRouterLLM()
        
        # Manually trigger the cycle logic (extracted from run_cycle)
        task = "Test Task"
        plan = agent.llm.think(task, agent.memory)
        result = "Mock Result"
        
        print("\n--- TEST REFLECT ---")
        reflection = agent.llm.reflect(task, plan, result)
        
        entry = {
            "timestamp": time.time(),
            "task": task,
            "plan": plan,
            "result": result,
            "reflection": reflection
        }
        agent.memory.append(entry)
        agent.save_memory()
        
        # Verify
        with open("memory.json", "r") as f:
            data = json.load(f)
            last_entry = data[-1]
            self.assertEqual(last_entry['task'], "Test Task")
            self.assertEqual(last_entry['reflection']['lesson'], "Mock lesson works!")
            print("\nSUCCESS: Memory saved correctly with reflection.")

if __name__ == '__main__':
    unittest.main()
