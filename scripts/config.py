#!/usr/bin/env python3
"""
Configuration management for awesome-claude-agents
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List

class Config:
    """Configuration manager for agent scraping."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.error(f"Failed to load config from {self.config_path}: {e}")
            return {}

    @property
    def agent_sources(self) -> List[Dict[str, Any]]:
        """Get enabled agent sources."""
        sources = self._config.get('agent_sources', [])
        return [source for source in sources if source.get('enabled', True)]

    @property
    def logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self._config.get('logging', {})

    @property
    def generation_config(self) -> Dict[str, Any]:
        """Get generation configuration."""
        return self._config.get('generation', {})

    def get_enabled_sources(self) -> List[Dict[str, Any]]:
        """Get all enabled sources with their configuration."""
        return self.agent_sources