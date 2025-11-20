"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

# Add src directory to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


# Configure pytest-asyncio
def pytest_configure(config):
    """Configure pytest settings."""
    config.option.asyncio_default_fixture_loop_scope = "function"
