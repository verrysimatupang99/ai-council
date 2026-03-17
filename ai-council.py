#!/usr/bin/env python3
"""
AI Council CLI - Main Entry Point with Robust Venv Detection
"""

import sys
import os
from pathlib import Path

def in_venv():
    """Check if the script is running inside a virtual environment"""
    return hasattr(sys, 'real_prefix') or (getattr(sys, 'base_prefix', sys.prefix) != sys.prefix)

def activate_venv():
    """Re-execute the script using the venv python if available"""
    if in_venv():
        return

    # Path to venv python
    script_dir = Path(__file__).parent.absolute()
    venv_python = script_dir / "venv" / "bin" / "python3"
    
    if venv_python.exists():
        # Use execv to replace the current process with the venv python
        # We use str(venv_python) instead of resolve() to keep the venv path
        os.execv(str(venv_python), [str(venv_python)] + sys.argv)

# Try to run via venv
activate_venv()

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

try:
    from ai_council.cli import cli
except ImportError as e:
    # If we still can't find dependencies, try one more fallback: 
    # check if we are in the project dir but the imports are failing
    print(f"❌ Error: Missing dependencies ({e}).")
    print(f"Make sure you have run './setup.sh' successfully.")
    sys.exit(1)

if __name__ == "__main__":
    cli()
