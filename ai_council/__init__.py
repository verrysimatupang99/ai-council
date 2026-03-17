"""
AI Council CLI - Multi-agent AI system for collaborative problem solving
"""

__version__ = "0.1.0"
__author__ = "AI Council Team"

from .core.config import Config
from .core.council import CouncilCoordinator
from .providers.base import BaseProvider

__all__ = ["Config", "CouncilCoordinator", "BaseProvider"]
