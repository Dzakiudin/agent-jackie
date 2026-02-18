# Agent Jackie 🧠🤖

**Agent Jackie** adalah eksperimen membangun *Self-Improving AI Agent* dari nol menggunakan Python. 
Dibangun dengan filosofi **"Anti-Goblok"**: Agent ini tidak hanya menjalankan perintah, tapi juga memiliki "hati nurani" untuk merenungkan hasil tindakannya (`Reflect`) dan belajar dari kesalahan (`Store Memory`).

## 🌟 Fitur Utama

1.  **Siklus Hidup Cerdas**:
    *   **PLAN**: Menganalisis tugas menggunakan LLM (DeepSeek R1 atau CodeLlama).
    *   **ACT**: Menjalankan perintah OS, membaca, atau menulis file.
    *   **OBSERVE**: Melihat output/error dari tindakan tersebut.
    *   **REFLECT**: Menganalisis apakah tindakan sukses dan menyimpan pelajaran (_lesson_) ke memori.


2.  **Tools (The Hands)**:
    *   `execute_command`: Eksekusi perintah terminal dengan **Safety Filter**.
    *   `read_file`: Membaca konten file untuk analisis.
    *   `write_file`: Membuat atau mengupdate file secara langsung.
    *   `search_web`: Mencari informasi real-time di internet (DuckDuckGo).

3.  **Memory (The Brain)**:
    *   **Retrieve**: Mengingat tugas masa lalu yang relevan menggunakan *Semantic Search* sederhana.
    *   **Reflect**: Menganalisis hasil kerja dan menyimpan pelajaran (_lesson_).
    *   **Store**: Menyimpan riwayat lengkap ke `memory.json`.

4.  **Interaction (The Mouth)**:
    *   **Final Answer**: Merangkum hasil kerja menjadi jawaban natural yang mudah dimengerti manusia.


## 🛠️ Instalasi

1.  **Clone Repository**
    ```bash
    git clone https://github.com/Dzakiudin/agent-jackie.git
    cd agent-jackie
    ```

2.  **Pilih "Otak" (LLM)**

    ### Opsi A: Pakai Local (Ollama) - Gratis & Offline 🏠
    *   Install [Ollama](https://ollama.com/).
    *   Download model: `ollama run codellama:7b-instruct-q4_K_M`.
    *   Edit `config.py`:
        ```python
        OPENROUTER_API_KEY = "dummy"
        OPENROUTER_URL = "http://localhost:11434/v1/chat/completions"
        MODEL_NAME = "codellama:7b-instruct-q4_K_M"
        ```

    ### Opsi B: Pakai Cloud (OpenRouter) ☁️
    *   Dapatkan API Key di [OpenRouter](https://openrouter.ai/).
    *   Edit `config.py`:
        ```python
        OPENROUTER_API_KEY = "sk-or-..." 
        OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
        MODEL_NAME = "deepseek/deepseek-r1"
        ```

3.  **Install Dependencies**
    ```bash
    pip install ddgs scikit-learn
    ```

## 🚀 Cara Menjalankan

Jalankan core loop agent:
```bash
python agent_core.py
```

## 📂 Struktur Project

*   `agent_core.py`: Otak utama (Loop Plan-Act-Reflect).
*   `tools.py`: Interaksi OS (baca/tulis file, command).
*   `memory.json`: Database pengetahuan agent.
*   `config.py`: Konfigurasi LLM.
*   `test_local_llm.py`: Script diagnosa koneksi Ollama.

## 🔮 Roadmap

- [x] Basic Loop (Plan-Act-Observe)
- [x] Reflection Layer
- [x] Safety Sandbox
- [x] Local LLM Support (Ollama)
- [x] Write File Tool
- [x] Internet Access (Search Tool)
- [x] Semantic Memory (Lite)
- [x] Final Answer (Conversational Response)

---
Built with code and conscience.

