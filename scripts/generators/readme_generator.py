#!/usr/bin/env python3
"""
README generator for awesome-claude-agents
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ReadmeGenerator:
    """Generate README.md from agent and repository data."""

    def __init__(self):
        self.repositories = []
        self.agents = []

    def add_repositories(self, repositories: List[Dict[str, Any]]):
        """Add repository data."""
        self.repositories.extend(repositories)

    def add_agents(self, agents: List[Dict[str, Any]]):
        """Add agent data."""
        self.agents.extend(agents)

    def generate_readme(self) -> str:
        """Generate the complete README content."""
        content = []

        # Header
        content.append("# Awesome Claude Agents")
        content.append("")
        content.append(f"A curated collection of **{len(self.agents)}** Claude agents from various repositories and sources.")
        content.append("")
        content.append(f"**Last updated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
        content.append("")

        # Installation instructions
        content.append("## Installation")
        content.append("")
        content.append("1. Install CAM: `curl -fsSL https://raw.githubusercontent.com/Chat2AnyLLM/code-assistant-manager/main/install.sh | bash`")
        content.append("2. `cam agent fetch`")
        content.append("3. `cam agent install security-auditor`")
        content.append("")

        # Category sections with tables
        agents_by_category = self._group_agents_by_category()
        categories = sorted(agents_by_category.keys())

        # Table of Contents
        if categories:
            content.append("## Table of Contents")
            content.append("")
            for category in categories:
                # GitHub-style anchor generation:
                # 1. Downcase
                # 2. Remove chars that are not a-z, 0-9, space, or hyphen
                # 3. Replace spaces with hyphens
                clean_cat = "".join(c for c in category.lower() if c.isalnum() or c in " -")
                anchor = clean_cat.replace(' ', '-')
                content.append(f"- [{category}](#{anchor})")
            content.append("")

        for category in categories:
            agents = agents_by_category[category]
            content.append(f"## {category}")
            content.append("")

            # Create a table for agents in this category
            content.append("| Agent | Description | Repository |")
            content.append("|-------|-------------|------------|")

            for agent in agents:
                name = agent.get('name', 'Unknown Agent')
                description = self._truncate_description(agent.get('description', 'No description available'))
                repo_owner = agent.get('repo_owner', '')
                repo_name = agent.get('repo_name', '')
                repo_url = f"https://github.com/{repo_owner}/{repo_name}"

                github_url = f"https://github.com/{repo_owner}/{repo_name}/blob/main/{agent.get('file_path', '')}"
                content.append(f"| [{name}]({github_url}) | {description} | [{repo_owner}/{repo_name}]({repo_url}) |")

            content.append("")

        # Footer
        content.append("---")
        content.append("")
        content.append("*This README is automatically generated from agent repository sources.*")
        content.append("")

        return "\n".join(content)

    def _group_agents_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group agents by category."""
        agents_by_category = {}
        for agent in self.agents:
            category = agent.get('category', 'General')
            if category not in agents_by_category:
                agents_by_category[category] = []
            agents_by_category[category].append(agent)
        return agents_by_category

    def _truncate_description(self, description: str, max_length: int = 100) -> str:
        """Truncate description to max length."""
        if len(description) <= max_length:
            return description
        return description[:max_length].rstrip() + "..."