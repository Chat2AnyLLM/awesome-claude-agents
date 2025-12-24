#!/usr/bin/env python3
"""
HTTP fetching utilities for agent data
"""

import requests
import json
import logging
import time
import hashlib
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class Fetcher:
    """HTTP data fetching utilities for agent repositories."""

    def __init__(self, timeout: int = 30, cache_ttl: int = 3600):
        self.timeout = timeout
        self.cache_ttl = cache_ttl  # Cache TTL in seconds (default 1 hour)
        self.session = requests.Session()
        self.cache: Dict[str, Dict[str, Any]] = {}  # URL -> {data, timestamp}

    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL."""
        return hashlib.md5(url.encode()).hexdigest()

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        if 'timestamp' not in cache_entry:
            return False
        return (time.time() - cache_entry['timestamp']) < self.cache_ttl

    def _get_cached_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if valid."""
        cache_key = self._get_cache_key(url)
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if self._is_cache_valid(cache_entry):
                logger.debug("Cache hit for: %s", url)
                return cache_entry['data']
            else:
                logger.debug("Cache expired for: %s", url)
                del self.cache[cache_key]
        return None

    def _set_cached_data(self, url: str, data: Dict[str, Any]):
        """Store data in cache."""
        cache_key = self._get_cache_key(url)
        self.cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }

    def fetch_json(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch JSON data from URL with caching and performance monitoring."""
        # Check cache first
        cached_data = self._get_cached_data(url)
        if cached_data is not None:
            return cached_data

        start_time = time.time()
        try:
            logger.info("Fetching data from: %s", url)
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            fetch_time = time.time() - start_time
            logger.info("Successfully fetched data from %s in %.2f seconds", url, fetch_time)

            # Cache the successful response
            self._set_cached_data(url, data)

            return data

        except requests.exceptions.RequestException as e:
            fetch_time = time.time() - start_time
            logger.error("Failed to fetch %s in %.2f seconds: %s", url, fetch_time, e)
            return None
        except json.JSONDecodeError as e:
            fetch_time = time.time() - start_time
            logger.error("Failed to parse JSON from %s in %.2f seconds: %s", url, fetch_time, e)
            return None

    def fetch_agent_repos_from_source(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch agent repository data from a configured source."""
        url = source_config.get("url")
        if not url:
            logger.error("No URL specified in source config")
            return []

        data = self.fetch_json(url)
        if not data:
            return []

        # The expected format is a dict with repo IDs as keys
        repos = []
        for repo_id, repo_data in data.items():
            if isinstance(repo_data, dict):
                repo_data["id"] = repo_id
                repo_data["source_url"] = url
                repos.append(repo_data)

        logger.info("Fetched %d agent repositories from %s", len(repos), url)
        return repos

    def fetch_agent_manifest(self, repo_owner: str, repo_name: str,
                           repo_branch: str = "main", agents_path: str = "agents") -> Optional[Dict[str, Any]]:
        """Fetch agents from a GitHub repository.

        Looks for agent files in the specified agents path.
        """
        # Try multiple branch names in order of popularity
        branch_attempts = [repo_branch]
        if repo_branch == "main":
            branch_attempts.extend(["master", "develop", "development", "dev"])
        elif repo_branch == "master":
            branch_attempts.extend(["main", "develop", "development", "dev"])

        for attempt_branch in branch_attempts:
            # First try to get directory listing
            api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{agents_path}?ref={attempt_branch}"
            try:
                logger.debug(f"Trying to fetch agent directory from {api_url}")
                response = self.session.get(api_url, timeout=self.timeout)
                response.raise_for_status()

                contents = response.json()
                if isinstance(contents, list):
                    # Extract agent files
                    agent_files = []
                    for item in contents:
                        if item.get('type') == 'file' and item.get('name', '').endswith('.md'):
                            agent_files.append({
                                'name': item['name'],
                                'path': item['path'],
                                'download_url': item['download_url']
                            })

                    if agent_files:
                        logger.info(f"Successfully fetched agent directory from {repo_owner}/{repo_name}")
                        return {'agent_files': agent_files}

            except requests.exceptions.RequestException as e:
                logger.debug(f"Failed to fetch directory from branch {attempt_branch}: {e}")
                continue

        logger.warning(f"No valid agent directory found in {repo_owner}/{repo_name}")
        return None

    def _validate_agent_index(self, data: Dict[str, Any]) -> bool:
        """Validate agent index structure."""
        if not isinstance(data, dict):
            return False

        # Check for common agent index patterns
        if "agents" in data and isinstance(data["agents"], list):
            return True
        if "items" in data and isinstance(data["items"], list):
            return True

        # If it's a direct list of agents
        if isinstance(data, list):
            return True

        return False

    def fetch_agents_from_repo(self, repo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch all agents from a repository."""
        agents = []

        repo_owner = repo_data.get("owner")
        repo_name = repo_data.get("name")
        repo_branch = repo_data.get("branch", "main")
        agents_path = repo_data.get("agentsPath", "agents")

        if not repo_owner or not repo_name:
            logger.warning("Missing repo information: %s", repo_data.get("id"))
            return agents

        # Fetch agent manifest (directory listing)
        agent_manifest = self.fetch_agent_manifest(repo_owner, repo_name, repo_branch, agents_path)

        if not agent_manifest:
            logger.warning("No agent manifest found for %s/%s", repo_owner, repo_name)
            return agents

        # Extract agent files and fetch their content
        agent_files = agent_manifest.get("agent_files", [])

        for agent_file in agent_files:
            try:
                # Download the markdown content
                download_url = agent_file.get('download_url')
                if not download_url:
                    continue

                logger.debug(f"Fetching agent file: {download_url}")
                response = self.session.get(download_url, timeout=self.timeout)
                response.raise_for_status()

                markdown_content = response.text

                # Parse agent data from markdown
                agent_data = self._parse_agent_markdown(markdown_content, agent_file['name'])

                if agent_data:
                    # Build agent entry with repository association
                    agent = {
                        "name": agent_data.get("name", agent_file['name'].replace('.md', '')),
                        "description": agent_data.get("description", ""),
                        "category": agent_data.get("category", "General"),
                        "author": agent_data.get("author"),
                        "version": agent_data.get("version", "1.0.0"),
                        "repo_owner": repo_owner,
                        "repo_name": repo_name,
                        "repo_url": f"https://github.com/{repo_owner}/{repo_name}",
                        "file_path": agent_file['path'],
                        "tags": agent_data.get("tags", []),
                        "source_data": agent_data
                    }
                    agents.append(agent)

            except requests.exceptions.RequestException as e:
                logger.warning(f"Failed to fetch agent file {agent_file['name']}: {e}")
                continue

        logger.info("Fetched %d agents from repository %s/%s", len(agents), repo_owner, repo_name)
        return agents

    def _parse_agent_markdown(self, content: str, filename: str) -> Optional[Dict[str, Any]]:
        """Parse agent data from markdown content."""
        try:
            # Basic parsing - look for YAML front matter or simple patterns
            lines = content.strip().split('\n')

            agent_data = {
                'name': filename.replace('.md', '').replace('-', ' ').title(),
                'description': '',
                'category': 'General'
            }

            # Try to extract description from first paragraph
            in_description = False
            description_lines = []

            for line in lines:
                line = line.strip()
                if line.startswith('# '):
                    # Title line - might override the filename-based name
                    title = line[2:].strip()
                    if title:
                        agent_data['name'] = title
                elif line and not line.startswith('#') and not in_description:
                    # Start of description
                    in_description = True
                    description_lines.append(line)
                elif line and in_description:
                    description_lines.append(line)
                elif not line and in_description:
                    # End of paragraph
                    break

            if description_lines:
                agent_data['description'] = ' '.join(description_lines).strip()

            return agent_data

        except Exception as e:
            logger.warning(f"Failed to parse agent markdown from {filename}: {e}")
            return None