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

        # Table of Contents
        toc = self._generate_table_of_contents()
        if toc:
            content.append("## Contents")
            content.append("")
            content.extend(toc)
            content.append("")

        # Agent Repositories table
        if self.repositories:
            content.append("## Agent Repositories")
            content.append("")
            content.append("| Repository | Description | Enabled |")
            content.append("|------------|-------------|---------|")

            for repo in self.repositories:
                repo_id = repo.get('id', 'unknown')
                owner = repo.get('owner', 'unknown')
                name = repo.get('name', 'unknown')
                enabled = "✅" if repo.get('enabled', True) else "❌"

                description = f"[{owner}/{name}](https://github.com/{owner}/{name})"
                content.append(f"| [{repo_id}](https://github.com/{owner}/{name}) | {description} | {enabled} |")

            content.append("")

        # Category sections with tables
        agents_by_category = self._group_agents_by_category()

        for category in sorted(agents_by_category.keys()):
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

                content.append(f"| [{name}](#{name.lower().replace(' ', '-').replace('/', '').replace('.', '')}) | {description} | [{repo_owner}/{repo_name}]({repo_url}) |")

            content.append("")

            # Detailed agent sections
            for agent in agents:
                content.extend(self._generate_agent_detail(agent))
                content.append("")

        # Footer
        content.append("---")
        content.append("")
        content.append("*This README is automatically generated from agent repository sources.*")
        content.append("")

        return "\n".join(content)

    def _generate_table_of_contents(self) -> List[str]:
        """Generate table of contents."""
        toc = []
        agents_by_category = self._group_agents_by_category()

        if self.repositories:
            toc.append("- [Agent Repositories](#agent-repositories)")

        for category in sorted(agents_by_category.keys()):
            category_anchor = category.lower().replace(' ', '-').replace(',', '').replace('&', 'and')
            toc.append(f"- [{category}](#{category_anchor})")

        return toc

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

    def _generate_agent_detail(self, agent: Dict[str, Any]) -> List[str]:
        """Generate detailed section for a single agent."""
        content = []

        name = agent.get('name', 'Unknown Agent')
        description = agent.get('description', '')
        author = agent.get('author', '')
        repo_owner = agent.get('repo_owner', '')
        repo_name = agent.get('repo_name', '')
        tags = agent.get('tags', [])

        content.append(f"### {name}")

        if author:
            content.append(f"**Author:** {author}")

        if repo_owner and repo_name:
            content.append(f"**Repository:** [{repo_owner}/{repo_name}](https://github.com/{repo_owner}/{repo_name})")

        if tags:
            content.append(f"**Tags:** {', '.join(tags)}")

        content.append("")
        content.append(description)

        return content