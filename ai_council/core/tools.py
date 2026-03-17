"""
Tool Manager for AI Council - Provides capabilities like file reading and search
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class ToolManager:
    """Provides tools that agents can use to interact with the real world"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.cwd()
        
    def read_file(self, file_path: str) -> str:
        """Read a file from the local system"""
        full_path = self.base_dir / file_path
        
        # Security check: Ensure path is within base_dir
        if not str(full_path.resolve()).startswith(str(self.base_dir.resolve())):
            return "Error: Access denied. Files must be within the project directory."
            
        try:
            if not full_path.exists():
                return f"Error: File '{file_path}' not found."
            
            # Don't read huge files
            if full_path.stat().st_size > 100000: # 100KB limit
                return "Error: File too large to read (max 100KB)."
                
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
                if item.name.startswith('.'): continue # Skip hidden
                files.append(item.name + ("/" if item.is_dir() else ""))
            return sorted(files)
        except Exception as e:
            return [f"Error: {str(e)}"]

    def get_tool_prompt(self) -> str:
        """Prompt to inject into system message to explain tool use"""
        return """
        CAPABILITY: You can ask to read files in the project.
        To read a file, include this in your response: [READ_FILE: path/to/file.py]
        To list files, include: [LIST_FILES: folder_name]
        The system will provide the content in the next turn.
        """
