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
        content.append("A curated collection of Claude agents from various repositories and sources.")
        content.append("")
        content.append(f"**Last updated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
        content.append("")
        content.append("---")
        content.append("")

        # Agent Repositories section
        if self.repositories:
            content.append("## Agent Repositories")
            content.append("")
            content.append(f"Found {len(self.repositories)} agent repositories:")
            content.append("")

            for repo in self.repositories:
                repo_id = repo.get('id', 'unknown')
                owner = repo.get('owner', 'unknown')
                name = repo.get('name', 'unknown')
                enabled = "✅" if repo.get('enabled', True) else "❌"
                agents_path = repo.get('agentsPath', 'agents')

                content.append(f"- **{repo_id}** {enabled}")
                content.append(f"  - Repository: [{owner}/{name}](https://github.com/{owner}/{name})")
                content.append(f"  - Agents Path: `{agents_path}`")
                content.append("")

        # Agents section
        if self.agents:
            content.append("## Agents")
            content.append("")
            content.append(f"Total agents collected: **{len(self.agents)}**")
            content.append("")

            # Group agents by category
            agents_by_category = {}
            for agent in self.agents:
                category = agent.get('category', 'General')
                if category not in agents_by_category:
                    agents_by_category[category] = []
                agents_by_category[category].append(agent)

            for category in sorted(agents_by_category.keys()):
                agents = agents_by_category[category]
                content.append(f"### {category} ({len(agents)} agents)")
                content.append("")

                for agent in agents:
                    name = agent.get('name', 'Unknown Agent')
                    description = agent.get('description', 'No description available')
                    author = agent.get('author', '')
                    repo_owner = agent.get('repo_owner', '')
                    repo_name = agent.get('repo_name', '')
                    tags = agent.get('tags', [])

                    content.append(f"#### {name}")
                    if author:
                        content.append(f"**Author:** {author}")
                    if repo_owner and repo_name:
                        content.append(f"**Repository:** [{repo_owner}/{repo_name}](https://github.com/{repo_owner}/{repo_name})")
                    if tags:
                        content.append(f"**Tags:** {', '.join(tags)}")
                    content.append("")
                    content.append(description)
                    content.append("")

        # Footer
        content.append("---")
        content.append("")
        content.append("*This README is automatically generated from agent repository sources.*")
        content.append("")

        return "\n".join(content)