#!/usr/bin/env bash
# Security scanning

set -e

echo "Running security scans..."

echo "→ Bandit (security linter)"
poetry run bandit -r src/ -f screen

echo "→ Safety (dependency vulnerabilities)"
poetry run safety check --json || true

echo "✓ Security scans complete!"
