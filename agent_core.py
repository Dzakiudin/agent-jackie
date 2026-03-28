
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
import re

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
You MUST respond with a RAW JSON object containing two keys: "thought" and "plan".
"thought": A short explanation of your reasoning.
"plan": A LIST of action objects.

Example:
{{
    "thought": "I need to create a file and then run it.",
    "plan": [
        {{
            "action": "write_file",
            "path": "hello.py",
            "content": "print('Hello')"
        }},
        {{
            "action": "execute_command",
            "command": "python hello.py"
        }}
    ]
}}
        """

        # 3. Request ke OpenRouter
        user_msg = f"Task: {task}"
        
        try:
            # Use the robust helper
            response = self._query_llm(system_prompt, user_msg)
            
            # 4. Handle Nested Plan Issues (CodeLlama quirk)
            if response.get("plan") and isinstance(response["plan"], dict):
                print("[DEBUG] Flattening nested plan structure.")
                return response # Return the whole object, let run_cycle handle it
            
            # If response is just the plan list (old style), wrap it
            if isinstance(response, list):
                return {"thought": "No thought provided.", "plan": response}
                
            return response
            
        except Exception as e:
            print(f"[ERROR] Thinking Failed: {e}")
            return {
                "thought": "LLM Error. I will do nothing.",
                "plan": [{ "action": "error", "command": str(e) }]
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
            try:
                # Find the first '{'
                start_index = content.find('{')
                if start_index != -1:
                    # Use raw_decode to parse just the first object
                    obj, end_index = json.JSONDecoder().raw_decode(content, idx=start_index)
                    return obj
            except json.JSONDecodeError:
                pass
            
            # Fallback: Just try parsing the whole thing
            return json.loads(content)



    def heal_code(self, task, error_msg, file_content=None):
        print(f"\n[HEALING] Attempting to fix code...")
        
        system_prompt = """
You are a Senior Python Developer.
Your goal is to FIX the code based on the error message.

STRICT RESPONSE FORMAT:
You MUST respond with a RAW JSON object containing "thought" and "plan".
"plan" must be a LIST of actions to fix the code (usually write_file).

Example:
{
    "thought": "The error is a missing import. I will add it.",
    "plan": [
        {
            "action": "write_file",
            "path": "script.py",
            "content": "import os\\n..."
        }
    ]
}
        """
        
        user_msg = f"""
ORIGINAL TASK: {task}
ERROR: {error_msg}
SOURCE CODE:
{file_content if file_content else "Not provided."}

Fix the code and return the JSON plan.
        """
        
        try:
            return self._query_llm(system_prompt, user_msg)
        except Exception as e:
            print(f"[ERROR] Healing Failed: {e}")
            return None

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
             # print(f"[ERROR] Reflection Failed: {e}")
             return {"success": False, "lesson": "Reflection failed.", "error": str(e)}

    def final_answer(self, task, result):
        print(f"\n[ANSWER] Formulating response...")
        
        system_prompt = """
You are a helpful AI Assistant named Jackie.
Your job is to summarize the RESULT of the TASK for the user.
- Keep it concise and friendly.
- If the result is a search list, summarize the key finding.
- If the result is a success message, confirm it.
- If the result is an error or "No action taken", report the failure honestly. DO NOT hallucinate actions you did not take.

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

            # ACT
            actions = []
            
            # Robust Logic to extract list of actions
            if isinstance(plan, dict):
                 if "plan" in plan and isinstance(plan["plan"], list):
                     actions = plan["plan"]
                 elif "plan" in plan and isinstance(plan["plan"], dict):
                      # Nested single plan
                      actions = [plan["plan"]]
                 else:
                     # Single plan object (legacy)
                     # Only if it has 'action' key
                     if 'action' in plan:
                        actions = [plan]
            elif isinstance(plan, list):
                actions = plan
            
            final_result = []

            if not actions:
                 print("[WARN] No valid actions found in plan.")
                 result = "No valid actions planned."
            else:
                for step in actions:
                    action_type = step.get('action')
                    thought = step.get('thought', 'Executing step...')
                    print(f"\n--- ACT: {thought} ---")
                    
                    step_result = "No action taken."

                    if action_type == 'execute_command':
                        cmd = step.get('command')
                        print(f"Executing: {cmd}")
                        
                        # 1. Try Execute
                        exec_result = tools.safe_execute(cmd)
                        
                        # 2. Check Success
                        if isinstance(exec_result, dict):
                            step_result = exec_result['output']
                            success = exec_result['success']
                            
                            # 3. SELF-HEALING LOOP
                            retries = 0
                            while not success and retries < 3:
                                print(f"\n[⚠️] Execution Failed. Entering Self-Healing Mode (Attempt {retries+1}/3)...")
                                error_msg = exec_result.get('error', 'Unknown Error')
                                
                                # Try to find relevant file to read for context
                                # optimization: simplistic regex to find .py file in command
                                target_file = None
                                match = re.search(r'\b\w+\.py\b', cmd)
                                file_content = ""
                                if match:
                                    target_file = match.group(0)
                                    file_content = tools.read_file(target_file)

                                # Ask LLM to fix
                                heal_plan = self.llm.heal_code(task, error_msg, file_content)
                                
                                if heal_plan:
                                    # Execute Healing Actions
                                    print("Applying Fix...")
                                    h_actions = []
                                    if isinstance(heal_plan, dict):
                                        h_actions = heal_plan.get('plan', [])
                                    elif isinstance(heal_plan, list):
                                        h_actions = heal_plan
                                    
                                    for h_step in h_actions:
                                        h_action = h_step.get('action')
                                        if h_action == 'write_file':
                                            tools.write_file(h_step.get('path'), h_step.get('content'))
                                            print(f"Fixed file: {h_step.get('path')}")
                                    
                                    # Retry Execution
                                    print(f"Retrying: {cmd}")
                                    exec_result = tools.safe_execute(cmd)
                                    step_result = exec_result['output']
                                    success = exec_result['success']
                                
                                retries += 1
                            
                            if success:
                                 print("[✅] Fix Succeeded!")
                            else:
                                 print("[❌] Heal Failed after 3 attempts.")

                        else:
                            # Legacy fallback if tools.py didn't return dict (shouldn't happen)
                            step_result = exec_result

                    
                    elif action_type == 'read_file':
                        path = step.get('path')
                        print(f"Reading: {path}")
                        step_result = tools.read_file(path)

                    elif action_type == 'write_file':
                        path = step.get('path')
                        content = step.get('content', '')
                        print(f"Writing: {path}")
                        step_result = tools.write_file(path, content)

                    elif action_type == 'search_web':
                        query = step.get('query')
                        print(f"Searching: {query}")
                        step_result = tools.search_web(query)
                    
                    elif action_type == 'error':
                        step_result = f"Error: {step.get('command')}"
                    
                    # OBSERVE (Step Level)
                    print(f"[Result]: {str(step_result)[:200]}..." if len(str(step_result)) > 200 else f"[Result]: {step_result}")
                    final_result.append(f"Action: {action_type}\nResult: {step_result}")

                # Consolidate results for reflection
                result = "\n---\n".join(final_result)
            
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
            answer = self.llm.final_answer(task, result)
            print(f"Jackie: {answer}")



if __name__ == "__main__":
    agent = SimpleAgent()
    agent.run_cycle()
