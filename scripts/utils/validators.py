#!/usr/bin/env python3
"""
Validation utilities for agent data
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Validator:
    """Validation utilities for agent and repository data."""

    @staticmethod
    def validate_json_data(data: Any) -> bool:
        """Basic validation that data is a valid JSON structure."""
        if not isinstance(data, (dict, list)):
            logger.error("Data is not a valid JSON structure")
            return False
        return True

    @staticmethod
    def validate_agent_repo_data(repo_data: Dict[str, Any]) -> bool:
        """Validate agent repository data structure."""
        required_fields = ['owner', 'name']
        for field in required_fields:
            if field not in repo_data:
                logger.error(f"Missing required field '{field}' in agent repo data")
                return False

        if not isinstance(repo_data.get('owner'), str) or not repo_data['owner'].strip():
            logger.error("Invalid owner field")
            return False

        if not isinstance(repo_data.get('name'), str) or not repo_data['name'].strip():
            logger.error("Invalid name field")
            return False

        return True

    @staticmethod
    def validate_agent_data(agent_data: Dict[str, Any]) -> bool:
        """Validate agent data structure."""
        if not isinstance(agent_data, dict):
            logger.error("Agent data is not a dictionary")
            return False

        if 'name' not in agent_data:
            logger.error("Missing required field 'name' in agent data")
            return False

        if not isinstance(agent_data.get('name'), str) or not agent_data['name'].strip():
            logger.error("Invalid name field in agent data")
            return False

        return True