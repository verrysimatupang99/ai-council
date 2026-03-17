"""
Tool Manager for AI Council - Provides capabilities like file reading, search, and code execution
"""

import os
import sys
import io
import contextlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS


class ToolManager:
    """Provides tools that agents can use to interact with the real world"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.cwd()
        
    def read_file(self, file_path: str) -> str:
        """Read a file from the local system"""
        full_path = self.base_dir / file_path
        
        # Security check
        if not str(full_path.resolve()).startswith(str(self.base_dir.resolve())):
            return "Error: Access denied. Files must be within project directory."
            
        try:
            if not full_path.exists():
                return f"Error: File '{file_path}' not found."
            
            if full_path.stat().st_size > 100000:
                return "Error: File too large (max 100KB)."
                
            with open(full_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
            
    def list_files(self, sub_dir: str = ".") -> List[str]:
        """List files in a directory"""
        target_dir = self.base_dir / sub_dir
        if not str(target_dir.resolve()).startswith(str(self.base_dir.resolve())):
            return ["Error: Access denied."]
            
        try:
            files = []
            for item in target_dir.iterdir():
                if item.name.startswith('.') or item.name == "venv" or item.name == "__pycache__":
                    continue
                files.append(item.name + ("/" if item.is_dir() else ""))
            return sorted(files)
        except Exception as e:
            return [f"Error: {str(e)}"]

    def web_search(self, query: str, max_results: int = 5) -> str:
        """Perform a web search using DuckDuckGo"""
        try:
            # The library has internally handled the transition, 
            # we just need to use it without triggering the warning if possible
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                if not results:
                    return "No search results found."
                
                output = f"Search results for: {query}\n\n"
                for i, r in enumerate(results, 1):
                    output += f"{i}. {r['title']}\n   {r['snippet']}\n   Source: {r['href']}\n\n"
                return output
        except Exception as e:
            return f"Error during web search: {str(e)}"

    def execute_python(self, code: str) -> str:
        """Execute Python code in a safe-ish local sandbox"""
        # Note: This is a local sandbox for developer convenience.
        # It uses a redirected stdout/stderr to capture output.
        output_buffer = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
                # Create a restricted global namespace
                safe_globals = {
                    "__builtins__": __builtins__,
                    "import": __import__,
                }
                exec(code, safe_globals)
            
            result = output_buffer.getvalue()
            return result if result else "Code executed successfully (no output)."
        except Exception as e:
            return f"Error during execution: {str(e)}"

    def get_tool_prompt(self) -> str:
        """Prompt to inject into system message to explain tool use"""
        return """
        CAPABILITIES:
        1. Read Files: Include [READ_FILE: path/to/file.py]
        2. List Files: Include [LIST_FILES: folder_name]
        3. Web Search: Include [SEARCH: search query] to get real-time info.
        4. Python Interpreter: Include [EXECUTE: python_code] to run and verify logic.
        
        Rules:
        - Only use tools when necessary.
        - You will receive tool outputs in the next discussion round.
        """
