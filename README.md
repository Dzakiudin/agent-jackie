# Agent Jackie 🧠🤖

**Agent Jackie** adalah eksperimen membangun *Self-Improving AI Agent* dari nol menggunakan Python dan DeepSeek R1.
Dibangun dengan filosofi **"Anti-Goblok"**: Agent ini tidak hanya menjalankan perintah, tapi juga memiliki "hati nurani" untuk merenungkan hasil tindakannya (`Reflect`) dan belajar dari kesalahan (`Store Memory`).

## 🌟 Fitur Utama

1.  **Siklus Hidup Cerdas**:
    *   **PLAN**: Menganalisis tugas menggunakan LLM (DeepSeek R1).
    *   **ACT**: Menjalankan perintah OS atau membaca file.
    *   **OBSERVE**: Melihat output/error dari tindakan tersebut.
    *   **REFLECT**: Menganalisis apakah tindakan sukses dan menyimpan pelajaran (_lesson_) ke memori.

2.  **Tools (The Hands)**:
    *   `execute_command`: Eksekusi perintah terminal dengan **Safety Filter** (mencegah perintah berbahaya seperti `rm -rf`).
    *   `read_file`: Membaca konten file untuk analisis.

3.  **Memory (The Brain)**:
    *   Menyimpan riwayat task, plan, result, dan reflection ke `memory.json`.
    *   Belajar dari pengalaman sebelumnya (Context-aware).

## 🛠️ Instalasi

1.  **Clone Repository**
    ```bash
    git clone https://github.com/Dzakiudin/agent-jackie.git
    cd agent-jackie
    ```

2.  **Setup Konfigurasi**
    Buat file `config.py` (file ini di-*ignore* oleh git demi keamanan):
    ```python
    # config.py
    OPENROUTER_API_KEY = "sk-or-..." # Masukkan API Key OpenRouter Anda
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    MODEL_NAME = "deepseek/deepseek-r1"
    ```

3.  **Install Dependencies**
    Agent ini sangat ringan, hanya butuh Python standard library (dan `urllib` bawaan).
    Tidak perlu `pip install` yang berat-berat dulu!

## 🚀 Cara Menjalankan

Jalankan core loop agent:
```bash
python agent_core.py
```

Saat muncul prompt `User (Input Task):`, cobalah perintah seperti:
*   *"Cek apakah ada file bernama 'rahasia.txt'."*
*   *"Buatkan file 'catatan.txt' isinya 'Hari ini saya belajar AI'."*
*   *"Baca file 'tools.py' dan jelaskan isinya."*

## 📂 Struktur Project

*   `agent_core.py`: Otak utama. Mengatur loop Plan-Act-Reflect.
*   `tools.py`: Kumpulan fungsi untuk interaksi OS (baca file, jalanin command).
*   `memory.json`: Database pengetahuan agent (Log & Lessons).
*   `config.py`: Konfigurasi sensitif (API Keys).

## 🔮 Roadmap

- [x] Basic Loop (Plan-Act-Observe)
- [x] Reflection Layer
- [x] Safety Sandbox
- [ ] Long-term Vector Memory
- [ ] Internet Access (Search Tool)
- [ ] Self-Correction Mechanism

---
Built with code and conscience.
