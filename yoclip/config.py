"""Configuration management for YoClip."""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import json


class Config:
    """Configuration manager for YoClip."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager."""
        if config_dir is None:
            config_dir = Path.home() / ".yoclip"
        
        self.config_dir = config_dir
        self.config_file = config_dir / "config.json"
        self._config: Dict[str, Any] = {}
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Load existing config
        self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._config = {}
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't write config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value
        self.save()
    
    def delete(self, key: str) -> None:
        """Delete configuration value."""
        if key in self._config:
            del self._config[key]
            self.save()


# Global config instance
config = Config()
