
import json
import time
import os
import sys
import urllib.request
import urllib.error
import config
import tools  # The Hands


# Force UTF-8 output for Windows Console
sys.stdout.reconfigure(encoding='utf-8')


class OpenRouterLLM:
    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.url = config.OPENROUTER_URL
        self.model = config.MODEL_NAME

    def think(self, task, memory):
        print(f"\n[LLM] Thinking with {self.model}...")
        
        # 1. Siapkan Context dari Memory (Sederhana dulu)
        memory_str = json.dumps(memory[-3:]) if memory else "No memory yet."
        
        # 2. Bangun System Prompt yang Kuat
        system_prompt = f"""
You are an AI Agent operating on a Windows machine.
Your goal is to help the user by breaking down tasks into Plans and Actions.

MEMORY (Last 3 interactions):
{memory_str}

TOOLS AVAILABLE:
- execute_command(command): Run a shell command.
- read_file(path): Read the contents of a file.

RESPONSE FORMAT:
You MUST respond with a VALID JSON object.
Examples:
{{
    "thought": "I need to check the config file.",
    "action": "read_file",
    "path": "config.py"
}}
{{
    "thought": "I will list files.",
    "action": "execute_command",
    "command": "dir"
}}
        """

        # 3. Request ke OpenRouter
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000" # OpenRouter butuh ini
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task}
            ]
        }
        
        try:
            req = urllib.request.Request(self.url, json.dumps(data).encode('utf-8'), headers)
            with urllib.request.urlopen(req) as response:
                result = json.load(response)
                content = result['choices'][0]['message']['content']
                
                # Coba bersihkan markdown ```json jika ada
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].strip()
                
                return json.loads(content)
        
        except Exception as e:
            print(f"[ERROR] LLM Failed: {e}")
            return {
                "thought": "LLM Error. I will do nothing.",
                "action": "error",
                "command": str(e)
            }

    def reflect(self, task, plan, result):
        print(f"\n[REFLECTION] Analyzing result...")
        
        system_prompt = """
You are an AI Agent's Conscience.
Analyze the recent action and its result.
Did it succeed? What did we learn?

RESPONSE FORMAT:
JSON ONLY.
{
    "success": true/false,
    "error_analysis": "Why it failed (if applicable)",
    "lesson": "A short, reusable rule for the future.",
    "confidence": 0.0 to 1.0
}
        """
        
        user_msg = f"""
TASK: {task}
PLAN: {json.dumps(plan)}
RESULT: {result}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ]
        }
        
        try:
            req = urllib.request.Request(self.url, json.dumps(data).encode('utf-8'), headers)
            with urllib.request.urlopen(req) as response:
                result = json.load(response)
                content = result['choices'][0]['message']['content']
                
                # Clean markdown
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].strip()
                
                return json.loads(content)
        except Exception as e:
             print(f"[ERROR] Reflection Failed: {e}")
             return {"success": False, "lesson": "Reflection failed.", "error": str(e)}


class SimpleAgent:
    def __init__(self):
        self.memory = self.load_memory()
        self.llm = OpenRouterLLM()  # Pakai yang asli sekarang
    
    def load_memory(self):
        if output := self._read_file("memory.json"):
            try:
                return json.loads(output)
            except:
                return []
        return []

    def _read_file(self, filename):
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    return f.read()
            except:
                return None
        return None

    def save_memory(self):
        with open("memory.json", "w") as f:
            json.dump(self.memory, f, indent=2)

    def run_cycle(self):
        print(f"Agent is ready. Using model: {config.MODEL_NAME}")
        print("Type 'exit' to stop.")
        
        while True:
            task = input("\nUser (Input Task): ")
            if task.lower() == 'exit':
                break
            
            # PLAN
            print("\n--- PLAN ---")
            plan = self.llm.think(task, self.memory)
            
            if 'thought' in plan:
                print(f"Prophecy: {plan['thought']}")
            else:
                print(f"Raw Response: {plan}")

            # ACT
            result = "No action taken."
            print("\n--- ACT ---")
            if plan.get('action') == 'execute_command':
                cmd = plan.get('command')
                print(f"Executing: {cmd}")
                
                # Execute for real!
                result = tools.safe_execute(cmd)
            
            elif plan.get('action') == 'read_file':
                path = plan.get('path')
                print(f"Reading: {path}")
                result = tools.read_file(path)


            
            # OBSERVE
            print("\n--- OBSERVE ---")
            print(f"Result: {result}")
            
            # REFLECT & STORE
            print("\n--- REFLECT ---")
            reflection = self.llm.reflect(task, plan, result)
            print(f"Lesson: {reflection.get('lesson')}")
            
            print("Storing to memory...")
            entry = {
                "timestamp": time.time(),
                "task": task,
                "plan": plan,
                "result": result,
                "reflection": reflection
            }
            self.memory.append(entry)
            self.save_memory()


if __name__ == "__main__":
    agent = SimpleAgent()
    agent.run_cycle()
