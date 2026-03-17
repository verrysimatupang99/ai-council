"""
Configuration management for AI Council
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


def _load_dotenv(dotenv_path: Path) -> Dict[str, str]:
    """Load environment variables from .env file"""
    env_vars = {}
    if dotenv_path.exists():
        with open(dotenv_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
    return env_vars


class Config:
    """Manages AI Council configuration"""
    
    # Point to project root (parent of ai_council package)
    DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "config.json"
    DEFAULT_DOTENV_PATH = Path(__file__).parent.parent.parent / ".env"
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config: Dict[str, Any] = {}
        self._env_overrides: Dict[str, Any] = {}
        
    def load(self) -> "Config":
        """Load configuration from file and .env"""
        # Load .env file first
        self._load_dotenv_file()
        
        # Load config from JSON
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                self._config = json.load(f)
        
        # Load API keys from environment variables (overrides .env)
        self._load_env_keys()
        
        return self
    
    def _load_dotenv_file(self):
        """Load environment variables from .env file"""
        dotenv_path = self.DEFAULT_DOTENV_PATH
        env_vars = _load_dotenv(dotenv_path)
        
        # Set environment variables from .env
        for key, value in env_vars.items():
            if key not in os.environ:
                os.environ[key] = value
    
    def _load_env_keys(self):
        """Load API keys from environment variables"""
        env_mappings = {
            "OPENROUTER_API_KEY": ("api_providers", "openrouter", "api_key"),
            "GROQ_API_KEY": ("api_providers", "groq", "api_key"),
            "CEREBRAS_API_KEY": ("api_providers", "cerebras", "api_key"),
            "MISTRAL_API_KEY": ("api_providers", "mistral", "api_key"),
            "GEMINI_API_KEY": ("api_providers", "gemini", "api_key"),
        }
        
        for env_var, (section, provider, key) in env_mappings.items():
            if env_var in os.environ:
                if section not in self._config:
                    self._config[section] = {}
                if provider not in self._config[section]:
                    self._config[section][provider] = {}
                self._config[section][provider][key] = os.environ[env_var]
    
    def get(self, *keys: str, default: Any = None) -> Any:
        """Get nested config value"""
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def get_enabled_api_providers(self) -> Dict[str, Dict]:
        """Get list of enabled API providers with their config"""
        providers = {}
        api_config = self._config.get("api_providers", {})
        
        for name, config in api_config.items():
            if config.get("enabled", False) and config.get("api_key"):
                providers[name] = config
        
        return providers
    
    def get_enabled_cli_providers(self) -> Dict[str, Dict]:
        """Get list of enabled CLI providers"""
        providers = {}
        cli_config = self._config.get("cli_providers", {})
        
        for name, config in cli_config.items():
            if config.get("enabled", False):
                providers[name] = config
        
        return providers
    
    def get_agent_roles(self) -> Dict[str, Dict]:
        """Get all agent role configurations"""
        return self._config.get("agent_roles", {})
    
    def get_council_settings(self) -> Dict[str, Any]:
        """Get council-wide settings"""
        return self._config.get("council_settings", {})
    
    def save(self, path: Optional[Path] = None):
        """Save configuration to file"""
        save_path = path or self.config_path
        with open(save_path, "w") as f:
            json.dump(self._config, f, indent=2)
    
    def is_configured(self) -> bool:
        """Check if at least one provider is configured"""
        return bool(self.get_enabled_api_providers() or self.get_enabled_cli_providers())
