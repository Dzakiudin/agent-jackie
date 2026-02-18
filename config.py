# config.py
# Simpan konfigurasi penting di sini. Jangan hardcode password di script utama.



# --- OPTION A: LOCAL (Ollama) ---
# OPENROUTER_API_KEY = "dummy"
OPENROUTER_URL = "http://localhost:11434/v1/chat/completions"
MODEL_NAME = "codellama:7b-instruct-q4_K_M"
MODEL_NAME = "llama3:8b" # Bisa ganti model Ollama lain di sini

# --- OPTION B: CLOUD (OpenRouter) ---
# OPENROUTER_API_KEY = "sk-or-YOUR-KEY-HERE"
# OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# MODEL_NAME = "deepseek/deepseek-r1" # Atau ganti "openai/gpt-4o"


