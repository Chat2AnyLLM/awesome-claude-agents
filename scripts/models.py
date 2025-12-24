#!/usr/bin/env python3
"""
Data models for Claude agents and repositories
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class AgentRepo:
    """Represents an agent repository."""
    owner: str
    name: str
    branch: str = "main"
    enabled: bool = True
    agents_path: str = "agents"
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentRepo':
        """Create AgentRepo from dictionary data."""
        return cls(
            owner=data.get('owner', ''),
            name=data.get('name', ''),
            branch=data.get('branch', 'main'),
            enabled=data.get('enabled', True),
            agents_path=data.get('agentsPath', 'agents'),
            description=data.get('description')
        )

@dataclass
class Agent:
    """Represents a Claude agent."""
    name: str
    description: str = ""
    category: str = "General"
    author: Optional[str] = None
    version: str = "1.0.0"
    repo_owner: str = ""
    repo_name: str = ""
    repo_url: str = ""
    file_path: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    @property
    def id(self) -> str:
        """Unique identifier for the agent."""
        return f"{self.repo_owner}/{self.repo_name}:{self.name}"

    @property
    def github_url(self) -> str:
        """GitHub URL for the agent."""
        return f"https://github.com/{self.repo_owner}/{self.repo_name}/blob/{self.file_path}"