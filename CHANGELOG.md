# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and repository setup
- Backup orchestrator observability component
  - Support for Restic, Borg, and ZFS send/recv backends
  - Job scheduling with APScheduler (cron-like expressions)
  - Retention policy management (daily/weekly/monthly)
  - Backup verification (check + test restore)
  - Prometheus metrics exporter (HTTP endpoint and textfile collector)
  - Grafana dashboard (Backups Compact Overview)
  - CLI interface for job management
- Disaster recovery drill lab component
  - Terraform and Vagrant infrastructure templates
  - Ansible playbooks for drill environment setup
  - Node loss and data corruption drill scenarios
  - RTO/RPO metrics calculation
  - Drill report generation (JSON and Markdown)
- AI assistance features
  - Backup policy suggestion helper
  - Prometheus alert rule generator
  - Drill report AI summary
  - Pluggable AI provider system (OpenAI, mock)
- Example configurations
  - Restic, Borg, and ZFS backup policies
  - Prometheus scrape configs
  - Drill scenario configs
- Documentation
  - Comprehensive README (English and Russian)
  - Legal and license compliance documentation
  - Contributing guidelines
  - Apache 2.0 LICENSE
- Testing infrastructure
  - Unit test suite with >80% coverage
  - Integration tests with stubbed backends
  - CI/CD with GitHub Actions
  - Security scanning (Bandit, Safety)
  - Quality checks (Ruff, Black, mypy)

### Changed
- N/A (initial release)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- No custom cryptography implementation
- All encryption delegated to external tools (restic/borg/ZFS)
- Environment variable-based secret management
- Drill lab operations isolated to test environments only

## [0.1.0] - TBD

Initial alpha release.

[Unreleased]: https://github.com/ranas-mukminov/secure-backups-drill-lab/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ranas-mukminov/secure-backups-drill-lab/releases/tag/v0.1.0
