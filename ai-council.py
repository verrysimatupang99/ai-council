#!/usr/bin/env python3
"""
AI Council CLI - Main Entry Point
"""

import sys
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_council.cli import cli

if __name__ == "__main__":
    cli()
