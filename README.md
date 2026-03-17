# AI Council CLI 🤖🏛️

A sophisticated multi-agent AI council system that leverages a hybrid architecture of Cloud APIs and Local CLI tools to provide comprehensive, cross-validated answers through collaborative discussion.

## ✨ Features

- **Hybrid Intelligence**: Combines high-reasoning Cloud APIs (Groq, OpenRouter, Gemini, Cerebras) with high-efficiency Local CLI tools (Codex, Qwen, Kilo).
- **Persistent Memory**: All sessions are automatically saved to a local SQLite database. Never lose a brilliant insight again.
- **Smart Token Optimizer**: Precise token counting using `tiktoken` and intelligent context compression to save costs and stay within context windows.
- **Tool Use (File Interaction)**: Agents can read and analyze your local project files directly to provide context-aware feedback.
- **Markdown Export**: Generate professional session reports in Markdown format with a single command.
- **Rich TUI**: Beautiful, real-time updating terminal interface powered by `rich`.
- **Setup Wizard**: Interactive installation script with CLI auto-detection and API key configuration.

## 📦 Quick Start

### 1. Installation
```bash
git clone https://github.com/verrysimatupang99/ai-council.git
cd ai-council
./setup.sh
```
The setup wizard will automatically detect your installed CLI tools and help you configure your API keys.

### 2. Basic Usage
```bash
# Single query to the default council
./ai-council.py ask -q "What are the best practices for Microservices?"

# Interactive debate mode (2 rounds)
./ai-council.py ask -q "Should I use Rust or Go for this project?" --debate --rounds 2

# Ask the council to review your code
./ai-council.py ask -q "Review the code in setup.sh for security risks" --debate
```

## 🛠️ Commands

- `ask`: Main command to interact with the council.
- `history`: View a list of previous discussion sessions.
- `view <session_id>`: See the full details of a past session.
- `export <session_id>`: Export a session to a `.md` file in `exports/`.
- `agents`: List all configured agents and their specialized roles.
- `test`: Verify your API keys and provider connectivity.
- `setup`: Run the interactive setup wizard.

## 🎭 Specialized Agents

| Agent | Provider | Role | Key Strength |
|-------|----------|------|--------------|
| **Architect** | Groq (Llama 3.3) | High-level System Design | Speed & Structure |
| **Lead Coder** | Codex CLI | Raw Implementation | Zero Latency, Code Focus |
| **Security Critic** | OpenRouter (Nemotron) | Security & Logic Review | 120B Parameter Reasoning |
| **Optimizer** | Gemini API (2.5 Flash) | Performance Tuning | Huge Context & Efficiency |
| **Researcher** | Gemini CLI | Technical Documentation | Local Exploration |
| **Reviewer** | Qwen CLI | Style & Maintainability | State-of-the-art Coding Benchmarks |
| **Analyst** | Cerebras (Llama 3.1) | Rapid Deep-dives | Instant Inference |
| **Advocate** | Kilo CLI | User Experience | Practicality |
| **Moderator** | OpenRouter (Nemotron) | Final Synthesis | Consensus Building |

## 🧩 Advanced: Tool Use

Relevant agents can interact with your file system by including these tags in their responses:
- `[READ_FILE: path/to/file.py]`: To read and analyze code.
- `[LIST_FILES: folder_name]`: To explore project structure.

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI Council CLI                       │
├─────────────────────────────────────────────────────────┤
│  Input: User Query + Optional Context                   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Council Coordinator                │   │
│  │    (Storage | Optimizer | Tool Manager)          │   │
│  └─────────────────────────────────────────────────┘   │
│           │              │              │               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  API Pool   │  │  CLI Pool   │  │  TUI Display│     │
│  │ (Groq, etc) │  │ (Local AI)  │  │ (Rich Live) │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
│  Output: Persistent Database + Markdown Report          │
└─────────────────────────────────────────────────────────┘
```

## 📝 License

MIT
