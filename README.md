# AI Council CLI

A multi-agent AI council system that leverages multiple AI providers (API + CLI) to provide comprehensive answers through collaborative discussion.

## Features

- **Hybrid Architecture**: Supports both API-based and CLI-based AI providers
- **Multiple Providers**: OpenRouter, Groq, Cerebras, Gemini, + CLI tools (Codex, Qwen, Kilo)
- **Role-based Agents**: Each AI has a specific role (Architect, Critic, Optimizer, etc.)
- **Debate Mode**: Agents can discuss and refine each other's suggestions
- **Rich TUI**: Beautiful terminal interface with real-time updates
- **Parallel Execution**: Multiple AI responses generated simultaneously

## Installation

```bash
cd ai-council
pip install -r requirements.txt
```

## Configuration

1. Copy the config template:
```bash
cp config.example.json config.json
```

2. Edit `config.json` with your API keys and CLI preferences.

## Usage

```bash
# Interactive mode
python ai-council.py

# Single query
python ai-council.py -q "What's the best architecture for X?"

# With specific agents
python ai-council.py -q "Review this code" --agents architect,critic

# Debate mode
python ai-council.py -q "Should I use Rust or Go?" --debate
```

## Available Agents

| Provider | Type | Best For |
|----------|------|----------|
| Groq | API | Fast responses, coding |
| Gemini | API/CLI | Analysis, research |
| Mistral | API | European perspective |
| Cerebras | API | Technical depth |
| OpenRouter | API | Multi-model access |
| Qwen CLI | CLI | Asian market insight |
| Codex CLI | CLI | Code generation |
| Kilo CLI | CLI | Alternative perspective |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI Council CLI                       │
├─────────────────────────────────────────────────────────┤
│  Input: User Query                                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Council Coordinator                │   │
│  └─────────────────────────────────────────────────┘   │
│           │              │              │               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  API Pool   │  │  CLI Pool   │  │  TUI Display│     │
│  │  (async)    │  │  (subprocess)│  │  (Rich)     │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
│  Output: Synthesized Recommendation                     │
└─────────────────────────────────────────────────────────┘
```

## License

MIT
