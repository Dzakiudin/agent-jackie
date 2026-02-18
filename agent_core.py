
import json
import time
import os
import sys
import urllib.request
import urllib.error
import subprocess
import shlex
import config
import tools  # The Hands
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


# Force UTF-8 output for Windows Console
sys.stdout.reconfigure(encoding='utf-8')


class OpenRouterLLM:
    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.url = config.OPENROUTER_URL
        self.model = config.MODEL_NAME

    def think(self, task, memory):
        print(f"Thinking about: {task}")
        
        # 1. Retrieve Relevant Memories (Simple Semantic Search)
        relevant_memories = []
        for entry in memory:
            # Check similarity with past tasks
            past_task = entry.get('task', '')
            score = similarity(task.lower(), past_task.lower())
            
            # Also check if lessons are relevant
            lesson = entry.get('reflection', {}).get('lesson', '')
            if score > 0.4 or (lesson and any(word in task.lower() for word in lesson.lower().split() if len(word) > 4)):
                relevant_memories.append(f"- Past Task: {past_task}\n  Result: {entry.get('result')}\n  Lesson: {lesson}")

        context_str = "\n".join(relevant_memories[-3:]) # Last 3 relevant
        
        # 1. Siapkan Context dari Memory (Sederhana dulu)
        memory_str = json.dumps(memory[-3:]) if memory else "No memory yet."
        
        # 2. Bangun System Prompt yang Kuat
        system_prompt = f"""
You are an intelligent OS Agent.
Your goal is to complete tasks by planning and executing actions.

MEMORY CONTEXT (Past Lessons):
{context_str if context_str else "No relevant past memories."}

MEMORY (Last 3 interactions):
{memory_str}

TOOLS AVAILABLE:
- execute_command(command): Run a shell command.
- read_file(path): Read the contents of a file.
- write_file(path, content): Create or overwrite a file with specific content.
- search_web(query): Search the internet for information.


STRICT RESPONSE FORMAT:
You MUST respond with a RAW JSON object. DO NOT include any explanations, DO NOT use markdown code blocks. 
Just the JSON.

Examples:
{{
    "thought": "I will create a greeting file.",
    "action": "write_file",
    "path": "hello.txt",
    "content": "Hello World!"
}}
{{
    "thought": "Checking directory.",
    "action": "execute_command",
    "command": "dir"
}}
        """

        # 3. Request ke OpenRouter
        user_msg = f"Task: {task}"
        
        try:
            # Use the robust helper
            response = self._query_llm(system_prompt, user_msg)
            
            # 4. Handle Nested Plan Issues (CodeLlama quirk)
            # Sometimes it returns { "task": "...", "plan": { "thought": "...", "action": "..." } }
            if response.get("plan") and isinstance(response["plan"], dict):
                print("[DEBUG] Flattening nested plan structure.")
                return response["plan"]
                
            return response
            
        except Exception as e:
            print(f"[ERROR] Thinking Failed: {e}")
            return {
                "thought": "LLM Error. I will do nothing.",
                "action": "error",
                "command": str(e)
            }

    def _query_llm(self, system_prompt, user_msg, json_mode=True):
        """
        Helper to call Ollama/OpenRouter and robustly extract JSON or Text.
        """
        import re

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            "max_tokens": 1000,
            "temperature": 0.1 if json_mode else 0.7 # Higher temp for creativity in text
        }
        
        req = urllib.request.Request(
            self.url,
            data=json.dumps(data).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result['choices'][0]['message']['content']
            
            if not json_mode:
                return content.strip()

            # --- ROBUST JSON EXTRACTION ---
            # 1. Try to find JSON block in markdown
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # 2. Try to find raw JSON object (First { ... } block only)
            # This regex looks for the first balanced curly braces
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    # If failed, try to be more aggressive: Find first '{' and last '}'
                    start = content.find('{')
                    end = content.rfind('}')
                    if start != -1 and end != -1:
                        return json.loads(content[start:end+1])
            
            # Fallback: Just try parsing the whole thing
            return json.loads(content)



    def reflect(self, task, plan, result):
        print(f"\n[REFLECTION] Analyzing result...")
        
        system_prompt = """
You are an AI Agent's Conscience.
Analyze the recent action and its result.
Did it succeed? What did we learn?

STRICT RESPONSE FORMAT:
You MUST respond with a RAW JSON object. DO NOT include any explanations.
Example:
{
    "success": true,
    "error_analysis": "None",
    "lesson": "Always verify inputs.",
    "confidence": 0.9
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

    def final_answer(self, task, result):
        print(f"\n[ANSWER] Formulating response...")
        
        system_prompt = """
You are a helpful AI Assistant named Jackie.
Your job is to summarize the RESULT of the TASK for the user.
- Keep it concise and friendly.
- If the result is a search list, summarize the key finding.
- If the result is a success message, confirm it.
- If the result is an error, explain what happened.

DO NOT output JSON. Just plain text.
        """
        
        user_msg = f"""
TASK: {task}
RESULT: {str(result)[:2000]}  # Truncate to avoid context limit
        """

        try:
            # Use text mode (json_mode=False)
            answer = self._query_llm(system_prompt, user_msg, json_mode=False)
            return answer
            
        except Exception as e:
             return f"Task completed. Result: {str(result)[:100]}..."



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


            elif plan.get('action') == 'write_file':
                path = plan.get('path')
                content = plan.get('content', '')
                print(f"Writing: {path}")
                result = tools.write_file(path, content)

            elif plan.get('action') == 'search_web':
                query = plan.get('query')
                print(f"Searching: {query}")
                result = tools.search_web(query)




            
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

            # FINAL ANSWER
            print("\n--- RESPONSE ---")
            answer = self.llm.final_answer(task, result)
            print(f"Jackie: {answer}")



if __name__ == "__main__":
    agent = SimpleAgent()
    agent.run_cycle()
