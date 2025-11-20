#!/usr/bin/env bash
# Linting and code quality checks

set -e

echo "Running code quality checks..."

echo "→ Black (code formatting)"
poetry run black --check src/ tests/ ai_providers/

echo "→ Ruff (linting)"
poetry run ruff check src/ tests/ ai_providers/

echo "→ MyPy (type checking)"
poetry run mypy src/

echo "✓ All lint checks passed!"
