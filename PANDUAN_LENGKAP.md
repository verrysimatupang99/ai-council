# 🤖 AI Council CLI - Panduan Lengkap

Sistem multi-agent AI yang memanfaatkan berbagai provider (API + CLI) untuk memberikan jawaban komprehensif melalui diskusi kolaboratif.

## ✨ Fitur Utama

- **Hybrid Architecture**: Support API-based dan CLI-based AI providers
- **Multiple Providers**: OpenRouter, Groq, Cerebras, Gemini
- **Role-based Agents**: Setiap AI punya spesialisasi (Architect, Critic, Optimizer, dll)
- **Debate Mode**: Agent bisa berdiskusi dan saling merespons
- **Rich TUI**: Interface terminal yang interaktif
- **Parallel Execution**: Multiple AI responses digenerate bersamaan

## 📦 Instalasi

### 1. Setup Awal

```bash
cd ai-council

# Buat virtual environment
python3 -m venv venv

# Aktifkan venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Konfigurasi API Keys

API keys sudah dipindahkan dari project `maxsignal_v2` dan siap digunakan:

- ✅ **OpenRouter**: `your_openrouter_api_key_here`
- ✅ **Groq**: `your_groq_api_key_here`
- ✅ **Cerebras**: `your_cerebras_api_key_here`
- ✅ **Gemini**: `your_gemini_api_key_here`

File konfigurasi sudah ada di `config.json` dan `.env`.

### 3. Verifikasi

```bash
# Test konfigurasi
./ai-council.py test

# Lihat agents yang tersedia
./ai-council.py agents
```

## 🎭 Agent Roles

| Agent | Provider | Role | Temperature |
|-------|----------|------|-------------|
| **Architect** | Groq | System design, arsitektur, best practices | 0.7 |
| **Critic** | OpenRouter | Code review, identifikasi masalah, edge cases | 0.5 |
| **Optimizer** | Gemini | Performance, efisiensi, optimisasi | 0.6 |
| **Researcher** | Cerebras | Deep technical insights, perbandingan alternatif | 0.7 |
| **Generalist** | OpenRouter | Advice praktis, balanced perspective | 0.8 |
| **Moderator** | OpenRouter | Sintesis final, rekomendasi kesimpulan | 0.5 |

## 🚀 Cara Penggunaan

### Mode 1: Single Query (Tanpa Debate)

```bash
# Interactive
./ai-council.py ask

# Direct query
./ai-council.py ask -q "Best architecture untuk microservices?"

# Dengan agents spesifik
./ai-council.py ask -q "Review code ini" -a architect -a critic
```

### Mode 2: Debate Mode (Multiple Rounds)

```bash
# Debate dengan 2 rounds
./ai-council.py ask -q "Rust vs Go untuk backend?" --debate --rounds 2

# Debate dengan 3 rounds + agents spesifik
./ai-council.py ask -q "SQL vs NoSQL?" --debate -r 3 -a architect -a researcher -a optimizer
```

### Mode 3: Simple CLI (Tanpa TUI)

```bash
./ai-council.py ask -q "Hello" --simple
```

## 📋 Contoh Use Cases

### 1. Code Review

```bash
./ai-council.py ask -q "
Review code Python berikut:

def fetch_data(url):
    import requests
    response = requests.get(url)
    return response.json()
" --debate
```

### 2. Architecture Decision

```bash
./ai-council.py ask -q "
Saya ingin build real-time chat application dengan:
- 10,000 concurrent users
- Low latency requirement
- Budget terbatas

Tech stack apa yang recommended?
" --debate -r 2
```

### 3. Learning & Research

```bash
./ai-council.py ask -q "
Jelaskan perbedaan antara:
- REST API
- GraphQL
- gRPC

Kapan menggunakan masing-masing?
" -a researcher -a generalist
```

## 🔧 Konfigurasi Lanjutan

### Edit Config

File: `config.json`

```json
{
  "api_providers": {
    "groq": {
      "enabled": true,
      "api_key": "your_key",
      "model": "llama-3.3-70b-versatile"
    }
  },
  "council_settings": {
    "default_agents": ["architect", "critic", "optimizer"],
    "max_debate_rounds": 2,
    "timeout_seconds": 60
  }
}
```

### Enable CLI Providers

Jika kamu ingin menggunakan CLI tools yang sudah terinstall:

```json
{
  "cli_providers": {
    "gemini_cli": {
      "enabled": true,
      "command": "gemini"
    },
    "qwen_cli": {
      "enabled": true,
      "command": "qwen"
    }
  }
}
```

## 🐛 Troubleshooting

### Error: "No providers configured"

```bash
# Check config file
cat config.json

# Check .env file
cat .env

# Verify dengan test
./ai-council.py test
```

### Error: "API key not configured"

Pastikan API keys sudah di-set di `config.json` atau `.env`:

```bash
export OPENROUTER_API_KEY=sk-or-v1-xxx
export GROQ_API_KEY=gsk_xxx
export GEMINI_API_KEY=AIzaSyxxx
```

### Error: "Command not found" (CLI providers)

Install CLI tools terlebih dahulu:

```bash
# Gemini CLI
npm install -g @google/gemini-cli

# Codex CLI
npm install -g @openai/codex

# Qwen CLI
# Check https://github.com/QwenLM/Qwen

# Kilo CLI
# Check documentation
```

## 📊 Struktur Project

```
ai-council/
├── ai_council/
│   ├── __init__.py
│   ├── cli.py              # Main CLI entry point
│   ├── core/
│   │   ├── config.py       # Configuration manager
│   │   └── council.py      # Council coordinator
│   ├── providers/
│   │   ├── base.py         # Base provider interface
│   │   ├── api_providers.py    # API providers
│   │   └── cli_providers.py    # CLI providers
│   └── ui/
│       └── tui.py          # Rich TUI interface
├── ai-council.py           # Executable script
├── config.json             # Main configuration
├── .env                    # Environment variables
├── requirements.txt
├── setup.sh
└── README.md
```

## 🎯 Tips & Best Practices

1. **Gunakan Debate Mode** untuk pertanyaan kompleks yang butuh multiple perspectives
2. **Pilih Agents** sesuai kebutuhan:
   - Coding problems → architect, critic, optimizer
   - Research → researcher, generalist
   - Decision making → semua agents + moderator
3. **Parallel Execution** otomatis aktif untuk response lebih cepat
4. **Temperature Settings** bisa disesuaikan di `config.json`

## 📝 License

MIT License - Feel free to use and modify!

## 🙏 Credits

API Keys migrated from:
- `maxsignal_v2` project
- `civ6-ai-agent` project

Created with ❤️ for collaborative AI problem-solving
