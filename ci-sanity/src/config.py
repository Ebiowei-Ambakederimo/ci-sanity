
import os
from typing import List, Dict, Any
import yaml


class Config:
    """Manages ci-sanity configuration."""

    DEFAULT_CONFIG = {
        'platform': 'github',
        'secrets': [],
        'strict': False,
    }

    def __init__(self, config_path: str = None):
        """Load config from file or use defaults."""
        self.data = self._load(config_path)

    def _load(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from file."""
        # Start with a shallow copy of defaults and ensure secrets is a fresh list
        config = self.DEFAULT_CONFIG.copy()
        config['secrets'] = list(config.get('secrets', []))

        # Try user-specified path
        if config_path and os.path.exists(config_path):
            user_config = self._read_yaml(config_path)
            if user_config:
                config.update(user_config)
            # Ensure secrets is always a list after merging
            config['secrets'] = list(config.get('secrets') or [])
            return config

        # Try default location
        default_path = '.ci-sanity.yml'
        if os.path.exists(default_path):
            user_config = self._read_yaml(default_path)
            if user_config:
                config.update(user_config)

        # Ensure secrets is always a list before returning
        config['secrets'] = list(config.get('secrets') or [])
        return config

    def _read_yaml(self, path: str) -> Dict[str, Any]:
        try:
            with open(path) as f:
                return yaml.safe_load(f) or {}
        except Exception:
            # Silently fail on config read errors - use defaults
            return {}

    @property
    def platform(self) -> str:
        """Get configured platform."""
        return self.data.get('platform', 'github')

    @property
    def secrets(self) -> List[str]:
        """Get list of declared secrets."""
        return self.data.get('secrets', [])

    @property
    def strict(self) -> bool:
        """Check if strict mode is enabled."""
        return bool(self.data.get('strict', False))

    def set_strict(self, strict: bool):
        """Enable or disable strict mode."""
        self.data['strict'] = bool(strict)