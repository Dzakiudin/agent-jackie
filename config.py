import os

# config.py
# Digunakan untuk menyimpan konfigurasi utama. 
# Secrets dipindahkan ke .env melalui environment variables.

# --- KONFIGURASI DEFAULT ---
DEFAULT_OPENROUTER_URL = "http://localhost:11434/v1/chat/completions"
DEFAULT_MODEL_NAME = "llama3:8b"

# --- ENV VARS ---
# Masukkan nilai ini ke file .env atau set di OS environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "dummy")
OPENROUTER_URL = os.getenv("OPENROUTER_URL", DEFAULT_OPENROUTER_URL)
MODEL_NAME = os.getenv("MODEL_NAME", DEFAULT_MODEL_NAME)
