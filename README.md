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

5.  **Self-Healing (The Immune System) 🚑**:
    *   **Auto-Detect**: Mendeteksi error saat eksekusi kode (cth: Syntax Error).
    *   **Auto-Fix**: Menganalisis error dan source code, lalu meminta LLM melakukan *rewrite* perbaikan.
    *   **Retry**: Mencoba menjalankan ulang kode yang sudah diperbaiki secara otomatis.

## 🛠️ Instalasi

1.  **Clone Repository**
    ```bash
    git clone https://github.com/Dzakiudin/agent-jackie.git
    cd agent-jackie
    ```

2.  **Pilih "Otak" (LLM)**

    Buka file `config.py` dan pilih salah satu opsi dengan *uncomment* baris yang sesuai.

    ### Opsi A: Local (Ollama) - Gratis & Offline 🏠
    *   **Keunggulan**: Privasi 100%, Gratis, Tidak butuh internet.
    *   **Cara**:
        1.  Install [Ollama](https://ollama.com/).
        2.  Download model (pilih salah satu):
            *   `ollama run codellama:7b-instruct-q4_K_M` (Coding)
            *   `ollama run llama3:8b` (General)
        3.  Update `config.py` bagian Opsi A.

    ### Opsi B: Cloud (OpenRouter) ☁️
    *   **Keunggulan**: Jauh lebih pintar, support model besar (DeepSeek R1, GPT-4, Claude).
    *   **Cara**:
        1.  Daftar di [OpenRouter](https://openrouter.ai/).
        2.  Dapatkan API Key.
        3.  Update `OPENROUTER_API_KEY` di `config.py` bagian Opsi B.

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

*   `agent_core.py`: Otak utama (Loop Plan-Act-Reflect-Heal).
*   `tools.py`: Interaksi OS (baca/tulis file, command, web search).
*   `memory.json`: Database pengetahuan agent.
*   `config.py`: Konfigurasi LLM.
*   `test_local_llm.py`: Script diagnosa koneksi Ollama.

## 🔮 Roadmap & Development Journey

- [x] **Phase 1: Basic Loop** (Plan-Act-Observe)
- [x] **Phase 2: Reflection Layer** (Self-Correction)
- [x] **Phase 3: Safety Sandbox** (Mencegah perintah berbahaya)
- [x] **Phase 4: Local LLM Support** (Ollama Integration)
- [x] **Phase 5: Tools Expansion** (Write File, Web Search)
- [x] **Phase 6: Semantic Memory** (Mengingat masa lalu)
- [x] **Phase 7: Multi-Step Automation** (Auto-Pilot / Chain of Thought)
- [x] **Phase 8: Self-Healing Code** (Memperbaiki error sendiri)

---
Built with code and conscience.

