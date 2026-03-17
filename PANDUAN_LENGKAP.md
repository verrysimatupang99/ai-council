# 🤖 AI Council CLI - Panduan Lengkap

Sistem multi-agent AI canggih yang menggabungkan kekuatan **Cloud API** (Penalaran Tinggi) dan **Local CLI** (Efisiensi Teknis) untuk memberikan jawaban yang telah divalidasi silang melalui diskusi kolaboratif.

## ✨ Fitur Utama

- **Arsitektur Hybrid**: Mendukung provider berbasis API (Groq, Gemini, OpenRouter, Cerebras) dan tool CLI lokal (Codex, Qwen, Kilo).
- **Persistent Memory**: Semua sesi diskusi disimpan otomatis ke database **SQLite** lokal.
- **Smart Token Optimizer**: Penghitungan token presisi menggunakan `tiktoken` dan kompresi konteks cerdas untuk menghemat biaya API.
- **Tool Use (File Interaction)**: Agent dapat membaca dan menganalisis file di dalam proyek Anda secara langsung.
- **Markdown Export**: Ekspor hasil diskusi menjadi laporan profesional dalam format `.md`.
- **Rich TUI**: Antarmuka terminal interaktif dengan update real-time yang memukau.

## 📦 Instalasi & Setup

### 1. Setup Otomatis (Direkomendasikan)

Gunakan Setup Wizard yang telah kami sediakan untuk konfigurasi instan:

```bash
git clone https://github.com/verrysimatupang99/ai-council.git
cd ai-council
chmod +x setup.sh
./setup.sh
```

Wizard ini akan:
- Membuat virtual environment dan menginstal dependensi.
- **Mendeteksi otomatis** tool AI CLI yang terpasang di sistem Anda.
- Meminta input **API Key** secara interaktif.
- Mengatur model terbaik berdasarkan plan Anda (**FREE** atau **PRO**).

## 🎭 Daftar Agen & Spesialisasi

Council ini terdiri dari 9 agen dengan peran yang telah dioptimalkan:

| Agen | Provider | Peran Utama | Keunggulan |
|-------|----------|-------------|------------|
| **Architect** | Groq | Desain Arsitektur | Kecepatan kilat & struktur solid |
| **Lead Coder** | Codex CLI | Implementasi Kode | Fokus pada sintaks & efisiensi lokal |
| **Security Critic** | OpenRouter | Review Keamanan | Logika penalaran 120B parameter |
| **Optimizer** | Gemini API | Optimasi Performa | Analisis context besar & efisiensi |
| **Researcher** | Gemini CLI | Riset Teknis | Eksplorasi dokumentasi lokal |
| **Reviewer** | Qwen CLI | Standarisasi Kode | Teliti terhadap best practices |
| **Analyst** | Cerebras | Analisis Cepat | Inferensi instan untuk masalah spesifik |
| **Advocate** | Kilo CLI | User Experience | Perspektif pengguna & kemudahan |
| **Moderator** | OpenRouter | Sintesis Final | Penengah diskusi & penarik kesimpulan |

## 🚀 Panduan Penggunaan

### Mode 1: Tanya Jawab Standar
```bash
./ai-council.py ask -q "Bagaimana cara mengamankan API di Node.js?"
```

### Mode 2: Mode Debat (Multi-Ronde)
Sangat direkomendasikan untuk masalah kompleks agar agen bisa saling mengoreksi.
```bash
./ai-council.py ask -q "Microservices vs Monolith untuk startup?" --debate --rounds 2
```

### Mode 3: Analisis Kode Lokal (Tool Use)
Anda bisa meminta agen untuk memeriksa file yang ada di folder proyek.
```bash
./ai-council.py ask -q "Review file setup.sh dan cari potensi bug" --debate
```
*Catatan: Agen akan menggunakan perintah `[READ_FILE: setup.sh]` secara otomatis.*

### Mode 4: Tanpa UI (Simple Mode)
Cocok untuk scripting atau output teks mentah.
```bash
./ai-council.py ask -q "Halo" --simple
```

## 📜 Manajemen Riwayat (History)

Semua diskusi Anda tidak akan hilang:

1.  **Lihat daftar riwayat**:
    ```bash
    ./ai-council.py history
    ```
2.  **Lihat detail sesi tertentu**:
    ```bash
    ./ai-council.py view <SESSION_ID>
    ```
3.  **Ekspor ke Markdown**:
    ```bash
    ./ai-council.py export <SESSION_ID>
    ```
    *File akan tersimpan di folder `exports/`.*

## 🔧 Konfigurasi Lanjutan

### File `config.json`
Anda dapat menyesuaikan `temperature`, `model`, dan agen default secara manual di file ini.

### Environment Variables (`.env`)
Jika lebih suka menggunakan environment variables, isi API Key di file `.env`:
```env
OPENROUTER_API_KEY=xxx
GROQ_API_KEY=xxx
CEREBRAS_API_KEY=xxx
GEMINI_API_KEY=xxx
```

## 📊 Struktur Proyek

```
ai-council/
├── ai_council/
│   ├── core/
│   │   ├── storage.py      # Database SQLite (Persistence)
│   │   ├── optimizer.py    # Token Manager (Tiktoken)
│   │   ├── tools.py        # File Interaction (Capabilities)
│   │   └── council.py      # Brain of the Council
│   ├── providers/          # API & CLI Implementation
│   └── ui/                 # Rich TUI Interface
├── exports/                # Hasil ekspor Markdown
├── setup.sh                # Setup Wizard
└── ai-council.py           # Entry Point Utama
```

## 📝 License

MIT License - Dibuat dengan ❤️ untuk solusi masalah melalui kolaborasi AI.

---
*Dokumentasi ini diperbarui secara otomatis pada Maret 2026.*
