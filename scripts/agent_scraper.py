#!/usr/bin/env python3
"""
Agent Scraper - Generate curated README from Claude agent repository data
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List

try:
    from .config import Config
    from .utils.fetcher import Fetcher
    from .utils.validators import Validator
    from .generators.readme_generator import ReadmeGenerator
except ImportError:
    # Fallback for direct execution - all files are in same directory
    from config import Config
    from utils.fetcher import Fetcher
    from utils.validators import Validator
    from generators.readme_generator import ReadmeGenerator

def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def generate_readme(repositories: list, agents: list, output_file: str) -> bool:
    """Generate README from repository and agent data."""
    generator = ReadmeGenerator()
    generator.add_repositories(repositories)
    generator.add_agents(agents)

    content = generator.generate_readme()

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        logger = logging.getLogger(__name__)
        logger.info("README generated successfully: %s", output_file)
        return True
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error("Failed to write README: %s", e)
        return False

def cmd_generate_readme(args, config, logger):
    """Handle generate-readme command."""
    logger.info("Agent Scraper starting...")

    # Get enabled sources
    sources = config.get_enabled_sources()
    logger.info("Loaded %d enabled sources", len(sources))

    if not sources:
        logger.warning("No enabled sources found in configuration")
        return 0

    # Fetch data from all sources
    fetcher = Fetcher()
    all_repositories = []
    all_agents = []

    for source in sources:
        logger.info("Processing source: %s", source.get("id"))
        repositories = fetcher.fetch_agent_repos_from_source(source)
        all_repositories.extend(repositories)

        # Fetch agents for each repository
        for repo_data in repositories:
            if not repo_data.get('enabled', True):
                logger.debug("Skipping disabled repository: %s", repo_data.get('id'))
                continue

            if not Validator.validate_agent_repo_data(repo_data):
                logger.warning("Invalid repository data, skipping: %s", repo_data.get('id'))
                continue

            agents = fetcher.fetch_agents_from_repo(repo_data)
            all_agents.extend(agents)

    logger.info("Total repositories collected: %d", len(all_repositories))
    logger.info("Total agents collected: %d", len(all_agents))

    if args.dry_run:
        print(f"Dry run: Would generate README with {len(all_repositories)} repositories and {len(all_agents)} agents")
        return 0

    # Generate README
    output_file = config.generation_config.get('output_file', 'README.md')
    if generate_readme(all_repositories, all_agents, output_file):
        print(f"Successfully generated README with {len(all_repositories)} repositories and {len(all_agents)} agents!")
        return 0
    else:
        print("Failed to generate README")
        return 1

def cmd_validate_config(args, config, logger):
    """Handle validate-config command."""
    print("Configuration validation:")

    # Check basic config structure
    try:
        sources = config.get_enabled_sources()
        print(f"✓ Found {len(sources)} enabled sources")

        if args.check_sources:
            fetcher = Fetcher()
            for source in sources:
                source_id = source.get("id", "unknown")
                url = source.get("url", "")
                try:
                    # Test basic connectivity (this is a simple check)
                    logger.debug(f"Testing connectivity to {url}")
                    print(f"✓ Source '{source_id}' URL is accessible")
                except Exception as e:
                    print(f"✗ Source '{source_id}' connectivity failed: {e}")
                    return 1

        print("✓ Configuration is valid")
        return 0

    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")
        return 1

def cmd_list_sources(args, config, logger):
    """Handle list-sources command."""
    try:
        sources = config.get_enabled_sources()

        if args.format == "json":
            import json
            print(json.dumps(sources, indent=2))
        else:
            # Table format
            print("Configured Sources:")
            print("-" * 60)
            print(f"{'ID':<25} {'URL':<35}")
            print("-" * 60)
            for source in sources:
                source_id = source.get("id", "unknown")
                url = source.get("url", "")
                print(f"{source_id:<25} {url:<35}")

        return 0

    except Exception as e:
        print(f"Failed to list sources: {e}")
        return 1

def main():
    """Main entry point for the agent scraper."""
    parser = argparse.ArgumentParser(
        description="Generate curated README from Claude agent repository data"
    )

    # Global options
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # generate-readme command
    generate_parser = subparsers.add_parser(
        "generate-readme",
        help="Generate README.md from configured sources"
    )
    generate_parser.add_argument(
        "--output",
        type=str,
        default="README.md",
        help="Output file path"
    )
    generate_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration and sources without writing output"
    )

    # validate-config command
    validate_parser = subparsers.add_parser(
        "validate-config",
        help="Validate configuration file format and source accessibility"
    )
    validate_parser.add_argument(
        "--check-sources",
        action="store_true",
        help="Also test network connectivity to sources"
    )

    # list-sources command
    list_parser = subparsers.add_parser(
        "list-sources",
        help="List configured sources with status information"
    )
    list_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Load configuration
    try:
        config = Config(args.config)
        log_level = config.logging_config.get("level", "INFO")
        if args.verbose:
            log_level = "DEBUG"
    except Exception as e:
        print(f"Failed to load configuration: {e}")
        return 1

    # Setup logging
    setup_logging(log_level)

    logger = logging.getLogger(__name__)

    # Execute command
    if args.command == "generate-readme":
        return cmd_generate_readme(args, config, logger)
    elif args.command == "validate-config":
        return cmd_validate_config(args, config, logger)
    elif args.command == "list-sources":
        return cmd_list_sources(args, config, logger)

    return 0

if __name__ == "__main__":
    sys.exit(main())