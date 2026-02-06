"""
Configuration Management for ShivAI

NOTE: This is a stub file. Full implementation needed based on config.example.yaml
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from pathlib import Path


@dataclass
class SpeechConfig:
    engine: str = "vosk"
    language: str = "hi-IN"
    timeout: int = 5


@dataclass
class TTSConfig:
    engine: str = "pyttsx3"
    rate: int = 160
    volume: float = 1.0


@dataclass
class ADBConfig:
    enabled: bool = False
    adb_path: str = "adb"
    auto_connect: bool = True


@dataclass
class WorkflowConfig:
    enabled: bool = True
    max_concurrent: int = 3
    state_persistence: bool = True


@dataclass
class PluginConfig:
    plugin_dirs: List[str] = field(default_factory=lambda: ["shivai/plugins"])
    auto_load: bool = True
    enabled_plugins: List[str] = field(default_factory=list)


@dataclass
class DatabaseConfig:
    path: str = "data/db/shivai.db"
    backup_enabled: bool = True


@dataclass
class Config:
    """Main configuration for ShivAI"""
    
    offline_mode: bool = True
    debug: bool = False
    log_level: str = "INFO"
    data_dir: str = "data"
    
    speech: SpeechConfig = field(default_factory=SpeechConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    adb: ADBConfig = field(default_factory=ADBConfig)
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
    plugin: PluginConfig = field(default_factory=PluginConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    def __init__(self, config_path: str = None):
        """Initialize config, optionally loading from YAML file"""
        # Initialize with defaults
        self.offline_mode = True
        self.debug = False
        self.log_level = "INFO"
        self.data_dir = "data"
        
        self.speech = SpeechConfig()
        self.tts = TTSConfig()
        self.adb = ADBConfig()
        self.workflow = WorkflowConfig()
        self.plugin = PluginConfig()
        self.database = DatabaseConfig()
        
        # TODO: Load from YAML file if provided
        if config_path:
            pass  # Implement YAML loading
