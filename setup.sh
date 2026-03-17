#!/bin/bash
# AI Council Setup Wizard with API & CLI Auto-Detection

set -e

echo "🤖 AI Council CLI - Setup Wizard"
echo "================================"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Copy config if it doesn't exist
if [ ! -f "config.json" ]; then
    echo "📋 Creating config.json from template..."
    cp config.example.json config.json
fi

echo ""
echo "🔑 API Key Configuration"
echo "-----------------------"
echo "Press Enter to skip any provider you don't use."
echo ""

read -p "Enter OpenRouter API Key: " OR_KEY
read -p "Enter Groq API Key: " GROQ_KEY
read -p "Enter Cerebras API Key: " CER_KEY
read -p "Enter Gemini API Key: " GEM_KEY

echo ""
echo "🌟 Plan Selection"
echo "----------------"
echo "Which AI plan do you use? (Affects default models)"
echo "1) FREE (Uses free-tier models: Nemotron, Llama 3.1 8B, Gemini Flash)"
echo "2) PRO/PAID (Uses premium models: Llama 3.3 70B, Gemini 2.5 Pro/Flash, etc.)"
read -p "Choice (1 or 2, default 1): " PLAN_CHOICE

PLAN="free"
if [ "$PLAN_CHOICE" == "2" ]; then
    PLAN="pro"
fi

echo ""
echo "🔍 Scanning for AI CLI tools..."
# List of CLI commands to check
CLI_COMMANDS=("gemini" "codex" "qwen" "kilo")
CLI_MAPPING=("gemini_cli" "codex_cli" "qwen_cli" "kilo_cli")
FOUND_CLIS=()

for i in "${!CLI_COMMANDS[@]}"; do
    CMD="${CLI_COMMANDS[$i]}"
    KEY="${CLI_MAPPING[$i]}"
    if command -v "$CMD" >/dev/null 2>&1; then
        echo "  ✅ Found $CMD CLI"
        FOUND_CLIS+=("$KEY")
    fi
done

echo ""
echo "⚙️  Updating config.json..."

# Use a small Python script to update the JSON safely
python3 <<EOF
import json
import os

config_path = 'config.json'
with open(config_path, 'r') as f:
    config = json.load(f)

# Update API Keys
if "$OR_KEY": config['api_providers']['openrouter']['api_key'] = "$OR_KEY"
if "$GROQ_KEY": config['api_providers']['groq']['api_key'] = "$GROQ_KEY"
if "$CER_KEY": config['api_providers']['cerebras']['api_key'] = "$CER_KEY"
if "$GEM_KEY": config['api_providers']['gemini']['api_key'] = "$GEM_KEY"

# Update Models based on Plan
if "$PLAN" == "free":
    config['api_providers']['openrouter']['model'] = "nvidia/nemotron-3-super-120b-a12b:free"
    config['api_providers']['groq']['model'] = "llama-3.3-70b-versatile"
    config['api_providers']['cerebras']['model'] = "llama3.1-8b"
    config['api_providers']['gemini']['model'] = "gemini-2.5-flash"
else:
    config['api_providers']['openrouter']['model'] = "openrouter/auto"
    config['api_providers']['groq']['model'] = "llama-3.3-70b-versatile"
    config['api_providers']['cerebras']['model'] = "llama3.1-8b"
    config['api_providers']['gemini']['model'] = "gemini-2.5-pro"

# Enable detected CLIs
found_clis = "${FOUND_CLIS[@]}".split()
if 'cli_providers' in config:
    for cli_key in found_clis:
        if cli_key in config['cli_providers']:
            config['cli_providers'][cli_key]['enabled'] = True
            print(f"    - Enabled {cli_key}")

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print("\n✅ config.json has been updated with your preferences.")
EOF

echo ""
echo "🎉 Setup complete!"
echo "You can now run: ./ai-council.py ask -q \"Your question\""
echo ""
