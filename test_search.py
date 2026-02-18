
import unittest
from tools import search_web
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

class TestWebSearch(unittest.TestCase):
    def test_search(self):
        print("\nTesting Web Search...")
        result = search_web("Who is the president of Indonesia 2024?")
        print(f"Result: {result}")
        self.assertNotEqual(result, "No results found.")
        self.assertIn("Prabowo", result) # Expecting Prabowo in results

if __name__ == '__main__':
    unittest.main()
