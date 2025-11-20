# Contributing to Secure Backups + Drill Lab

Thank you for your interest in contributing to this project! We welcome contributions from the community.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions. We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/).

## How to Contribute

### Reporting Bugs

1. Check existing [GitHub Issues](https://github.com/ranas-mukminov/secure-backups-drill-lab/issues) to avoid duplicates
2. Open a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, tool versions)
   - Relevant logs or error messages

### Suggesting Features

1. Open an issue labeled "enhancement"
2. Describe the use case and motivation
3. Provide examples of how the feature would be used
4. Consider backward compatibility

### Pull Requests

1. **Fork the repository** and create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Set up development environment**:
   ```bash
   poetry install --with dev
   poetry shell
   ```

3. **Make your changes**:
   - Follow the code style guidelines (see below)
   - Write tests for new functionality
   - Update documentation as needed

4. **Run quality checks**:
   ```bash
   ./scripts/lint.sh
   pytest tests/
   ./scripts/security_scan.sh
   ```

5. **Commit your changes**:
   - Use clear, descriptive commit messages
   - Reference issue numbers when applicable
   - Sign your commits (optional but recommended)

6. **Push to your fork** and open a pull request:
   - Provide a clear description of changes
   - Link to related issues
   - Include screenshots/examples if applicable

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8 with 100-character line length
- **Formatting**: Use Black for auto-formatting
- **Linting**: Code must pass Ruff and mypy checks
- **Type hints**: All functions must have type annotations

Run formatters and linters:
```bash
black src/ tests/
ruff check src/ tests/ --fix
mypy src/
```

### Testing

- **Unit tests**: Required for all new functionality
- **Coverage**: Aim for >80% code coverage
- **Test isolation**: Use mocks for external tool CLIs
- **Naming**: Use descriptive test names (e.g., `test_backup_job_handles_missing_source_directory`)

Run tests:
```bash
pytest tests/ -v --cov=src --cov-report=html
```

### Documentation

- **Docstrings**: Use Google-style docstrings for all public functions/classes
- **README**: Update README.md if adding user-facing features
- **Examples**: Add example configs for new features
- **Comments**: Explain "why" not "what" in complex logic

Example docstring:
```python
def calculate_rto(failure_time: datetime, recovery_time: datetime) -> timedelta:
    """Calculate Recovery Time Objective (RTO) for a drill.

    Args:
        failure_time: When the failure was injected
        recovery_time: When the service was fully restored

    Returns:
        Time delta representing the RTO

    Raises:
        ValueError: If recovery_time is before failure_time
    """
    ...
```

### Security

- **No secrets in code**: Use environment variables for all credentials
- **No custom crypto**: Only use encryption from external tools (restic/borg/ZFS)
- **Input validation**: Validate all user inputs and config files
- **Safe defaults**: Default to secure configurations
- **Audit logs**: Log security-relevant operations

### License Compliance

- All contributions must be compatible with Apache 2.0
- Do not copy code from incompatible licenses
- Only interact with external tools via their CLIs/APIs
- Document any new third-party dependencies in LEGAL.md

## Project Structure

```
src/
  backup_orchestrator_observability/  # Backup orchestrator core
  backup_disaster_drill_lab/          # DR drill lab
ai_providers/                         # AI provider abstractions
examples/                             # Example configurations
tests/                                # Test suite
scripts/                              # Development scripts
```

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ranas-mukminov/secure-backups-drill-lab.git
   cd secure-backups-drill-lab
   ```

2. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**:
   ```bash
   poetry install --with dev --extras ai
   ```

4. **Install external tools** (for integration tests):
   ```bash
   # Ubuntu/Debian
   sudo apt install restic borgbackup zfsutils-linux
   
   # macOS
   brew install restic borgbackup openzfs
   ```

5. **Run tests**:
   ```bash
   poetry run pytest
   ```

## Release Process

(Maintainers only)

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with release notes
3. Create git tag: `git tag -a v0.1.0 -m "Release v0.1.0"`
4. Push tag: `git push origin v0.1.0`
5. GitHub Actions will automatically build and publish

## Getting Help

- **Documentation**: See [README.md](README.md)
- **Issues**: Open a GitHub issue
- **Discussion**: Use GitHub Discussions for questions
- **Contact**: https://run-as-daemon.ru

## Recognition

Contributors will be acknowledged in the project README and release notes.

---

Thank you for contributing! 🚀
