
import json
import io
import sys
from agent_core import OpenRouterLLM, similarity

# Mock Memory
mock_memory = [
    {
        "task": "What is the capital of Indonesia?",
        "result": "Jakarta",
        "reflection": {"lesson": "Capital cities are important facts."}
    },
    {
        "task": "How to cook fried rice?",
        "result": "Use rice and soy sauce.",
        "reflection": {"lesson": "Cooking requires ingredients."}
    }
]

def test_memory_retrieval():
    print("\n--- Testing Memory Retrieval ---")
    task = "List facts about Indonesia's capital."
    
    # Simulate logic from agent_core.py
    relevant_memories = []
    for entry in mock_memory:
        past_task = entry.get('task', '')
        score = similarity(task.lower(), past_task.lower())
        
        lesson = entry.get('reflection', {}).get('lesson', '')
        # Simple overlap check
        if score > 0.4 or (lesson and any(word in task.lower() for word in lesson.lower().split() if len(word) > 4)):
            relevant_memories.append(f"Found: {past_task} (Score: {score:.2f})")
            
    if relevant_memories:
        print("SUCCESS: Retrieved relevant memories.")
        for m in relevant_memories:
            print(m)
    else:
        print("FAIL: No memory retrieved (Expected 'Indonesia').")

if __name__ == "__main__":
    test_memory_retrieval()
