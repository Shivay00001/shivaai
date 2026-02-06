"""
ShivAI Core Engine Package

This package contains the core agent orchestration system, plugin loader,
command parser, context management, and task queue.

Offline-first, modular, plugin-based architecture.
"""

__version__ = "1.0.0"
__author__ = "ShivAI Team"

from .agent import ShivAIAgent
from .plugin_loader import PluginLoader, BasePlugin
from .task_queue import TaskQueue

__all__ = [
    "ShivAIAgent",
    "PluginLoader",
    "BasePlugin",
    "TaskQueue",
]
