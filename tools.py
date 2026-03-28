import subprocess
import shlex
import os


def safe_execute(command):
    """
    Safely executes a command with a timeout.
    Returns: dict {'success': bool, 'output': str, 'error': str}
    """
    print(f"[TOOL] Executing safely: {command}")
    
    # 1. Blacklist Check (Simple Protection)
    forbidden = ["rm ", "del ", "format ", "rd ", "shutdown"]
    if any(bad in command.lower() for bad in forbidden) and "echo" not in command.lower():
        return {
            "success": False,
            "output": f"Error: Command '{command}' is blacklisted for safety.",
            "error": "Blacklisted command"
        }

    try:
        # 2. Execute with Timeout
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            timeout=30, 
            shell=True,
            encoding='utf-8', 
            errors='replace'
        )
        
        output = result.stdout + result.stderr
        success = result.returncode == 0
        
        return {
            "success": success,
            "output": output.strip() if output else "Command executed with no output.",
            "error": result.stderr if not success else ""
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "Error: Command timed out (30s limit).",
            "error": "Timeout"
        }
    except Exception as e:
        return {
            "success": False,
            "output": f"Error: {e}",
            "error": str(e)
        }

def read_file(path):
    """
    Safely reads a file from the system.
    """
    print(f"[TOOL] Reading file: {path}")
    try:
        # 1. Size Check (Don't read massive files)
        if os.path.getsize(path) > 100000: # 100KB limit
            return "Error: File too large (>100KB). Read a specific section or use grep."
            
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{path}' not found."
    except Exception as e:
        return f"Error: {e}"

def write_file(path, content):
    """
    Safely writes content to a file.
    """
    print(f"[TOOL] Writing file: {path}")
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error: {e}"

def search_web(query):
    """
    Searches the web using DuckDuckGo.
    """
    print(f"[TOOL] Searching web: {query}")
    try:
        from ddgs import DDGS
        results = DDGS().text(query, max_results=3)

        if results:
            return str(results)
        return "No results found."
    except Exception as e:
        return f"Error searching web: {e}"




