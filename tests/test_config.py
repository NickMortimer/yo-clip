"""Tests for configuration management."""

import json
import tempfile
from pathlib import Path
from yoclip.config import Config


def test_config_initialization():
    """Test config initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "test_config"
        config = Config(config_dir)
        
        assert config.config_dir == config_dir
        assert config.config_dir.exists()


def test_config_set_and_get():
    """Test setting and getting config values."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "test_config"
        config = Config(config_dir)
        
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"


def test_config_get_default():
    """Test getting config with default value."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "test_config"
        config = Config(config_dir)
        
        assert config.get("nonexistent_key", "default") == "default"


def test_config_delete():
    """Test deleting config values."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "test_config"
        config = Config(config_dir)
        
        config.set("test_key", "test_value")
        config.delete("test_key")
        assert config.get("test_key") is None


def test_config_persistence():
    """Test config persistence across instances."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / "test_config"
        
        # Create first config instance and set value
        config1 = Config(config_dir)
        config1.set("persistent_key", "persistent_value")
        
        # Create second config instance and check value
        config2 = Config(config_dir)
        assert config2.get("persistent_key") == "persistent_value"
