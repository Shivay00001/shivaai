"""
Tests for Plugin Loader System

Tests plugin discovery, loading, manifest validation, and lifecycle management.
"""

import pytest
import os
import json
import tempfile
from pathlib import Path

from shivai.core_engine.plugin_system.plugin_loader import (
    PluginLoader,
    BasePlugin,
    PluginManifest
)


class MockPlugin(BasePlugin):
    """Mock plugin for testing"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.initialized = False
        self.shutdown_called = False
    
    def initialize(self):
        self.initialized = True
        return True
    
    def shutdown(self):
        self.shutdown_called = True
    
    def get_capabilities(self):
        return ["mock_capability"]
    
    def handle_command(self, command, context):
        return f"Mock handled: {command}"


class TestPluginLoader:
    """Test suite for PluginLoader"""
    
    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def mock_plugin_structure(self, temp_plugin_dir):
        """Create mock plugin structure"""
        plugin_path = os.path.join(temp_plugin_dir, "mock_plugin")
        os.makedirs(plugin_path)
        
        # Create manifest
        manifest = {
            "name": "mock_plugin",
            "version": "1.0.0",
            "description": "Mock plugin for testing",
            "author": "Test",
            "plugin_class": "plugin.MockPlugin",
            "capabilities": ["mock_capability"]
        }
        
        with open(os.path.join(plugin_path, "manifest.json"), 'w') as f:
            json.dump(manifest, f)
        
        # Create plugin.py
        plugin_code = '''
from shivai.core_engine.plugin_loader import BasePlugin

class MockPlugin(BasePlugin):
    def initialize(self):
        return True
    
    def get_capabilities(self):
        return ["mock_capability"]
    
    def handle_command(self, command, context):
        return f"Mock handled: {command}"
'''
        with open(os.path.join(plugin_path, "plugin.py"), 'w') as f:
            f.write(plugin_code)
        
        return temp_plugin_dir
    
    def test_plugin_discovery(self, mock_plugin_structure):
        """Test plugin discovery"""
        loader = PluginLoader([mock_plugin_structure])
        discovered = loader.discover_plugins()
        
        assert len(discovered) == 1
        assert "mock_plugin" in discovered
    
    def test_manifest_loading(self, mock_plugin_structure):
        """Test manifest loading and validation"""
        loader = PluginLoader([mock_plugin_structure])
        loader.discover_plugins()
        
        assert "mock_plugin" in loader.manifests
        manifest = loader.manifests["mock_plugin"]
        
        assert manifest.name == "mock_plugin"
        assert manifest.version == "1.0.0"
        assert "mock_capability" in manifest.capabilities
    
    def test_plugin_loading(self, mock_plugin_structure):
        """Test plugin loading"""
        loader = PluginLoader([mock_plugin_structure])
        loader.discover_plugins()
        
        success = loader.load_plugin("mock_plugin")
        assert success
        assert "mock_plugin" in loader.plugins
    
    def test_plugin_unloading(self, mock_plugin_structure):
        """Test plugin unloading"""
        loader = PluginLoader([mock_plugin_structure])
        loader.discover_plugins()
        loader.load_plugin("mock_plugin")
        
        success = loader.unload_plugin("mock_plugin")
        assert success
        assert "mock_plugin" not in loader.plugins
    
    def test_get_plugin_by_capability(self, mock_plugin_structure):
        """Test getting plugins by capability"""
        loader = PluginLoader([mock_plugin_structure])
        loader.discover_plugins()
        loader.load_plugin("mock_plugin")
        
        plugins = loader.get_plugins_by_capability("mock_capability")
        assert len(plugins) == 1
    
    def test_enable_disable_plugin(self, mock_plugin_structure):
        """Test enable/disable plugin"""
        loader = PluginLoader([mock_plugin_structure])
        loader.discover_plugins()
        loader.load_plugin("mock_plugin")
        
        # Disable
        success = loader.disable_plugin("mock_plugin")
        assert success
        assert not loader.plugins["mock_plugin"].enabled
        
        # Enable
        success = loader.enable_plugin("mock_plugin")
        assert success
        assert loader.plugins["mock_plugin"].enabled
    
    def test_load_all_plugins(self, mock_plugin_structure):
        """Test loading all discovered plugins"""
        loader = PluginLoader([mock_plugin_structure])
        loader.discover_plugins()
        
        loaded_count = loader.load_all()
        assert loaded_count == 1
    
    def test_list_plugins(self, mock_plugin_structure):
        """Test listing all plugins"""
        loader = PluginLoader([mock_plugin_structure])
        loader.discover_plugins()
        
        plugins = loader.list_plugins()
        assert len(plugins) == 1
        assert plugins[0]['name'] == "mock_plugin"
    
    def test_get_plugin_info(self, mock_plugin_structure):
        """Test getting plugin info"""
        loader = PluginLoader([mock_plugin_structure])
        loader.discover_plugins()
        loader.load_plugin("mock_plugin")
        
        info = loader.get_plugin_info("mock_plugin")
        assert info is not None
        assert info['name'] == "mock_plugin"
        assert info['loaded'] is True
        assert info['enabled'] is True
    
    def test_nonexistent_plugin(self):
        """Test handling of nonexistent plugin"""
        loader = PluginLoader([])
        
        success = loader.load_plugin("nonexistent")
        assert not success
    
    def test_invalid_manifest(self, temp_plugin_dir):
        """Test handling of invalid manifest"""
        plugin_path = os.path.join(temp_plugin_dir, "invalid_plugin")
        os.makedirs(plugin_path)
        
        # Create invalid manifest (missing required fields)
        manifest = {
            "name": "invalid_plugin"
            # Missing other required fields
        }
        
        with open(os.path.join(plugin_path, "manifest.json"), 'w') as f:
            json.dump(manifest, f)
        
        loader = PluginLoader([temp_plugin_dir])
        discovered = loader.discover_plugins()
        
        # Should not discover plugin with invalid manifest
        assert "invalid_plugin" not in discovered
