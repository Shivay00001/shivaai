"""
Plugin Loader for ShivAI

Dynamically discovers and loads plugins from plugin directories.
Each plugin is a self-contained module with manifest.json metadata.

Provides plugin lifecycle management: load, enable, disable, unload.
"""

import os
import json
import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PluginManifest:
    """Plugin metadata from manifest.json"""
    name: str
    version: str
    description: str
    author: str
    plugin_class: str  # e.g., "plugin.VoskSpeechPlugin"
    capabilities: List[str]  # e.g., ["speech_recognition", "hindi_support"]
    dependencies: List[str] = None
    config_schema: Dict[str, Any] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.config_schema is None:
            self.config_schema = {}


class BasePlugin:
    """
    Base class for all ShivAI plugins
    
    Plugins must inherit from this class and implement required methods.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize plugin
        
        Args:
            config: Plugin configuration dictionary
        """
        self.config = config or {}
        self.enabled = True
    
    def initialize(self) -> bool:
        """
        Initialize plugin resources
        
        Called once when plugin is loaded.
        
        Returns:
            True if initialization successful, False otherwise
        """
        return True
    
    def shutdown(self) -> None:
        """
        Cleanup plugin resources
        
        Called when plugin is unloaded or application exits.
        """
        pass
    
    def get_capabilities(self) -> List[str]:
        """
        Get list of capabilities this plugin provides
        
        Returns:
            List of capability strings
        """
        return []
    
    def handle_command(self, command: str, context: Dict[str, Any]) -> Any:
        """
        Handle command directed to this plugin
        
        Args:
            command: Command string
            context: Execution context
            
        Returns:
            Command result (any type)
        """
        raise NotImplementedError("Plugin must implement handle_command()")


class PluginLoader:
    """
    Plugin discovery and loading system
    
    Features:
    - Auto-discovery of plugins in specified directories
    - Manifest validation
    - Dependency resolution
    - Plugin lifecycle management
    - Safe plugin isolation
    """
    
    def __init__(self, plugin_dirs: List[str] = None):
        """
        Initialize plugin loader
        
        Args:
            plugin_dirs: List of directories to search for plugins
        """
        self.plugin_dirs = plugin_dirs or ["shivai/plugins"]
        
        self.plugins: Dict[str, BasePlugin] = {}
        self.manifests: Dict[str, PluginManifest] = {}
        self.plugin_paths: Dict[str, str] = {}
        
        logger.info(f"PluginLoader initialized with dirs: {self.plugin_dirs}")
    
    def discover_plugins(self) -> List[str]:
        """
        Discover all plugins in plugin directories
        
        Returns:
            List of discovered plugin names
        """
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                logger.warning(f"Plugin directory not found: {plugin_dir}")
                continue
            
            # Iterate through subdirectories
            for item in os.listdir(plugin_dir):
                item_path = os.path.join(plugin_dir, item)
                
                if not os.path.isdir(item_path):
                    continue
                
                # Look for manifest.json
                manifest_path = os.path.join(item_path, "manifest.json")
                
                if os.path.exists(manifest_path):
                    try:
                        manifest = self._load_manifest(manifest_path)
                        
                        plugin_name = manifest.name
                        self.manifests[plugin_name] = manifest
                        self.plugin_paths[plugin_name] = item_path
                        
                        discovered.append(plugin_name)
                        logger.info(f"Discovered plugin: {plugin_name} v{manifest.version}")
                    
                    except Exception as e:
                        logger.error(f"Failed to load manifest from {manifest_path}: {e}")
        
        logger.info(f"Discovered {len(discovered)} plugins")
        return discovered
    
    def _load_manifest(self, manifest_path: str) -> PluginManifest:
        """Load and validate plugin manifest"""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required fields
        required_fields = ['name', 'version', 'description', 'author', 'plugin_class']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        return PluginManifest(**data)
    
    def load_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> bool:
        """
        Load and initialize plugin
        
        Args:
            plugin_name: Name of plugin to load
            config: Plugin configuration
            
        Returns:
            True if loaded successfully, False otherwise
        """
        if plugin_name in self.plugins:
            logger.warning(f"Plugin already loaded: {plugin_name}")
            return True
        
        if plugin_name not in self.manifests:
            logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        manifest = self.manifests[plugin_name]
        plugin_path = self.plugin_paths[plugin_name]
        
        try:
            # Check dependencies
            if not self._check_dependencies(manifest.dependencies):
                logger.error(f"Missing dependencies for plugin: {plugin_name}")
                return False
            
            # Import plugin module
            plugin_class = self._import_plugin_class(plugin_path, manifest.plugin_class)
            
            if not plugin_class:
                logger.error(f"Failed to import plugin class: {manifest.plugin_class}")
                return False
            
            # Instantiate plugin
            plugin_instance = plugin_class(config or {})
            
            # Initialize
            if not plugin_instance.initialize():
                logger.error(f"Plugin initialization failed: {plugin_name}")
                return False
            
            # Store plugin
            self.plugins[plugin_name] = plugin_instance
            
            logger.info(f"✅ Loaded plugin: {plugin_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def _import_plugin_class(self, plugin_path: str, plugin_class: str) -> Optional[Type[BasePlugin]]:
        """
        Dynamically import plugin class
        
        Args:
            plugin_path: Path to plugin directory
            plugin_class: Class path (e.g., "plugin.MyPlugin")
            
        Returns:
            Plugin class or None if import fails
        """
        try:
            # Add plugin path to sys.path temporarily
            if plugin_path not in sys.path:
                sys.path.insert(0, plugin_path)
            
            # Parse class path
            module_name, class_name = plugin_class.rsplit('.', 1)
            
            # Import module
            module_path = os.path.join(plugin_path, f"{module_name}.py")
            
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get class
            plugin_class_obj = getattr(module, class_name)
            
            return plugin_class_obj
        
        except Exception as e:
            logger.error(f"Failed to import plugin class {plugin_class}: {e}")
            return None
        
        finally:
            # Remove from sys.path
            if plugin_path in sys.path:
                sys.path.remove(plugin_path)
    
    def _check_dependencies(self, dependencies: List[str]) -> bool:
        """
        Check if all dependencies are available
        
        Args:
            dependencies: List of dependency names
            
        Returns:
            True if all dependencies available, False otherwise
        """
        if not dependencies:
            return True
        
        for dep in dependencies:
            if dep not in self.plugins:
                logger.warning(f"Missing dependency: {dep}")
                return False
        
        return True
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload plugin and cleanup resources
        
        Args:
            plugin_name: Name of plugin to unload
            
        Returns:
            True if unloaded successfully, False otherwise
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin not loaded: {plugin_name}")
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            plugin.shutdown()
            
            del self.plugins[plugin_name]
            
            logger.info(f"Unloaded plugin: {plugin_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            return True
        return False
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get plugin instance by name"""
        return self.plugins.get(plugin_name)
    
    def get_plugins_by_capability(self, capability: str) -> List[BasePlugin]:
        """
        Get all plugins that provide a specific capability
        
        Args:
            capability: Capability string (e.g., "speech_recognition")
            
        Returns:
            List of plugin instances
        """
        matching = []
        
        for plugin_name, plugin in self.plugins.items():
            if not plugin.enabled:
                continue
            
            if capability in plugin.get_capabilities():
                matching.append(plugin)
        
        return matching
    
    def load_all(self, enabled_only: bool = True) -> int:
        """
        Load all discovered plugins
        
        Args:
            enabled_only: Only load plugins marked as enabled
            
        Returns:
            Number of successfully loaded plugins
        """
        loaded_count = 0
        
        for plugin_name, manifest in self.manifests.items():
            if enabled_only and not manifest.enabled:
                logger.info(f"Skipping disabled plugin: {plugin_name}")
                continue
            
            if self.load_plugin(plugin_name):
                loaded_count += 1
        
        logger.info(f"Loaded {loaded_count}/{len(self.manifests)} plugins")
        return loaded_count
    
    def unload_all(self) -> None:
        """Unload all plugins"""
        plugin_names = list(self.plugins.keys())
        
        for plugin_name in plugin_names:
            self.unload_plugin(plugin_name)
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get plugin information"""
        if plugin_name not in self.manifests:
            return None
        
        manifest = self.manifests[plugin_name]
        loaded = plugin_name in self.plugins
        enabled = self.plugins[plugin_name].enabled if loaded else manifest.enabled
        
        return {
            'name': manifest.name,
            'version': manifest.version,
            'description': manifest.description,
            'author': manifest.author,
            'capabilities': manifest.capabilities,
            'dependencies': manifest.dependencies,
            'loaded': loaded,
            'enabled': enabled,
            'path': self.plugin_paths.get(plugin_name)
        }
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all discovered plugins"""
        return [
            self.get_plugin_info(name)
            for name in self.manifests.keys()
        ]
