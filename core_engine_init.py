"""
ShivAI Core Engine Package

This package contains the core agent orchestration system, plugin loader,
command parser, context management, and task queue.

Offline-first, modular, plugin-based architecture.
"""

__version__ = "1.0.0"
__author__ = "ShivAI Team"

from .agent import ShivAIAgent
from .plugin_loader import PluginLoader
from .command_parser import CommandParser
from .context_manager import ContextManager
from .task_queue import TaskQueue
from .config import Config

__all__ = [
    "ShivAIAgent",
    "PluginLoader",
    "CommandParser",
    "ContextManager",
    "TaskQueue",
    "Config",
]
