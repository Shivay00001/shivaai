"""
ShivAI - Autonomous General Intelligence

India's First Offline Expert Assistant - Your Personal Jarvis

Main package providing offline AI assistant capabilities:
- Voice recognition (Hindi + English)
- PC and Android automation
- App builder
- Multi-step workflows
- Pattern learning
"""

__version__ = "1.0.0"
__author__ = "ShivAI Team"
__license__ = "MIT"

from .core_engine import ShivAIAgent, PluginLoader, BasePlugin

__all__ = [
    "ShivAIAgent",
    "PluginLoader",
    "BasePlugin",
    "__version__",
]
