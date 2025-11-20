# Secure Backups + Drill Lab 🔒🚀

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Production-ready backup orchestration with observability + automated disaster recovery drills**

A comprehensive open-source project for managing secure, encrypted backups with **Prometheus metrics**, **Grafana dashboards**, and an automated **disaster recovery drill lab** for testing your backup/restore procedures.

**Author:** [Ranas Mukminov](https://run-as-daemon.ru) | **License:** Apache-2.0

---

## 🎯 Features

### Backup Orchestrator with Observability

- **Multi-backend support**: Restic, Borg Backup, ZFS send/recv
- **Flexible scheduling**: Cron-like expressions via APScheduler
- **Smart retention**: Hourly/daily/weekly/monthly/yearly policies
- **Automated verification**: Repository checks + test restores
- **Prometheus metrics**: Last backup time, duration, size, errors
- **Grafana dashboards**: Compact backup overview with RPO tracking
- **CLI management**: Simple command-line interface for all operations

### Disaster Recovery Drill Lab

- **Automated testing**: Node loss & data corruption scenarios
- **RTO/RPO measurement**: Precise recovery time tracking
- **Infrastructure as Code**: Terraform + Vagrant + Ansible
- **Drill reports**: JSON és Markdown summaries
- **AI-powered analysis**: Optional AI-generated recommendations

### AI Assistance (Optional)

- **Policy suggestions**: Generate backup configs from natural language
- **Alert rules**: Auto-generate Prometheus alerting rules
- **Drill summaries**: Executive summaries of DR test results

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/ranas-mukminov/secure-backups-drill-lab.git
cd secure-backups-drill-lab

# Install with Poetry
poetry install

# Or install with AI features
poetry install --extras ai

# Activate virtual environment
poetry shell
```

### Prerequisites

Install backup tools:

```bash
# Ubuntu/Debian
sudo apt install restic borgbackup zfsutils-linux

# macOS
brew install restic borgbackup openzfs

# Arch Linux
sudo pacman -S restic borg-backup zfs-utils
```

### Basic Usage

1. **Create a backup configuration**:

```yaml
# config.yaml
jobs:
  - name: home-backup
    backend: restic
    sources:
      - /home/user/Documents
    repository: /mnt/backups/restic/home
    schedule: "0 2 * * *"  # Daily at 2 AM
    retention:
      keep_daily: 7
      keep_weekly: 4
      keep_monthly: 6
    rpo_hours: 24

metrics:
  enabled: true
  port: 9090
```

2. **Start the orchestrator**:

```bash
# Set repository password
export RESTIC_PASSWORD="your-secure-password"

# Run orchestrator
backup-orchestrator run --config config.yaml
```

3. **View metrics**:

```bash
# Metrics endpoint
curl http://localhost:9090/metrics

# Import Grafana dashboard
# Import: src/backup_orchestrator_observability/grafana/dashboards/backups_compact_overview.json
```

4. **Manual backup**:

```bash
# Run specific job immediately
backup-orchestrator exec home-backup --config config.yaml

# Verify backup
backup-orchestrator verify home-backup --config config.yaml

# List all jobs
backup-orchestrator list-jobs --config config.yaml
```

---

## 📊 Monitoring & Dashboards

### Prometheus Metrics

The orchestrator exposes these metrics:

- `backup_last_success_timestamp{job}` - Timestamp of last successful backup
- `backup_duration_seconds{job}` - Backup duration
- `backup_bytes_transferred{job}` - Bytes transferred
- `backup_repository_size_bytes{job}` - Total repository size
- `backup_job_status{job}` - Current job status (enum)
- `backup_verification_success{job}` - Verification status (1=success, 0=fail)
- `backup_errors_total{job}` - Total error count

### Grafana Dashboard

Import the provided dashboard for visualization:

**Path:** `src/backup_orchestrator_observability/grafana/dashboards/backups_compact_overview.json`

**Features:**
- Bar gauges showing backup age vs RPO threshold
- State timeline of backup success/failure
- Repository size trends
- Backup duration charts
- Error rate monitoring
- Verification status table

---

## 🧪 Disaster Recovery Drill Lab

Test your backup/restore procedures automatically!

### Local Lab (Vagrant)

```bash
cd src/backup_disaster_drill_lab/vagrant

# Start lab environment
vagrant up

# Run node loss drill
drill-runner run --scenario node-loss-basic --config ../examples/drills/node-loss-basic.yaml

# View drill report
cat reports/drill-report-*.md

# Cleanup
vagrant destroy -f
```

### Cloud Lab (Terraform)

```bash
cd src/backup_disaster_drill_lab/terraform

# Initialize Terraform
terraform init

# Provision drill environment
terraform apply

# Run drill (see drill-runner CLI)
drill-runner run --scenario data-corruption --config ../examples/drills/corruption-basic.yaml

# Cleanup
terraform destroy
```

### RTO/RPO Metrics

Each drill measures:
- **RTO** (Recovery Time Objective): Time from failure to full restoration
- **RPO** (Recovery Point Objective): Time between last backup and failure

Reports include:
- Timeline of events
- Data integrity verification
- Resource usage
- Recommendations for improvement

---

## 🤖 AI Features (Optional)

Enable AI assistance by installing with extras and setting your API key:

```bash
# Install with AI support
poetry install --extras ai

# Set OpenAI API key
export OPENAI_API_KEY="sk-..."

# Generate backup policy
backup-orchestrator ai policy --description "Daily PostgreSQL backup to S3, keep 30 days"

# Generate alert rules
backup-orchestrator ai alerts --rpo-hours 24 > alerts.yaml

# Get drill summary with recommendations
drill-runner run --scenario node-loss --with-ai-summary
```

---

## 📖 Configuration Examples

See [`examples/policies/`](examples/policies/) for complete examples:

- **Restic**: [`simple-restic-home.yaml`](examples/policies/simple-restic-home.yaml) - Home directory to S3
- **Borg**: [`simple-borg-server.yaml`](examples/policies/simple-borg-server.yaml) - Server data to local repo
- **ZFS**: [`zfs-send-offsite.yaml`](examples/policies/zfs-send-offsite.yaml) - Incremental snapshots to offsite pool

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│     Backup Orchestrator                 │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │  Restic  │  │   Borg   │  │  ZFS   ││
│  │  Backend │  │  Backend │  │Backend ││
│  └────┬─────┘  └─────┬────┘  └───┬────┘│
│       │              │            │     │
│       └──────────────┴────────────┘     │
│                  │                      │
│           ┌──────▼──────┐               │
│           │  Scheduler  │               │
│           └──────┬──────┘               │
│                  │                      │
│         ┌────────▼─────────┐            │
│         │   Job Registry   │            │
│         └────────┬─────────┘            │
│                  │                      │
│         ┌────────▼──────────┐           │
│         │ Metrics Exporter  │           │
│         └────────┬──────────┘           │
└──────────────────┼───────────────────────┘
                   │
         ┌─────────▼───────────┐
         │    Prometheus       │
         └─────────┬───────────┘
                   │
         ┌─────────▼───────────┐
         │      Grafana        │
         └─────────────────────┘
```

---

## 🧪 Development

### Setup

```bash
# Install dependencies
poetry install --with dev --extras ai

# Run tests
poetry run pytest tests/ -v --cov

# Lint code
./scripts/lint.sh

# Security scan
./scripts/security_scan.sh
```

### Running Tests

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# With coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## 📜 License & Legal

This project is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for details.

**Important:**
- This project **does not include** any third-party backup tool code
- Restic, Borg, and ZFS are called as external CLI tools only
- See [LEGAL.md](LEGAL.md) for license compliance details

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Quick checklist:**
- Follow code style (Black, Ruff, mypy)
- Add tests for new features
- Update documentation
- Pass CI checks

---

## 🔒 Security

- **No custom cryptography** - All encryption via backup tools (restic/borg/ZFS native)
- **Environment variables** for secrets (no hardcoded passwords)
- **Drill lab isolation** - Never run destructive tests on production systems
- **Security scanning** - Automated Bandit + Safety checks in CI

Report security issues to: https://run-as-daemon.ru

---

## 📚 Resources

- **Documentation**: This README + in-code docstrings
- **Examples**: [`examples/`](examples/) directory
- **Author**: https://run-as-daemon.ru
- **Issues**: [GitHub Issues](https://github.com/ranas-mukminov/secure-backups-drill-lab/issues)

---

## 🌟 Roadmap

- [x] Multi-backend support (Restic, Borg, ZFS)
- [x] Prometheus metrics + Grafana dashboards
- [x] Disaster recovery drill lab
- [ ] Web UI for job management
- [ ] Backup catalog/search functionality
- [ ] Additional drill scenarios (database corruption, network partitions)
- [ ] Backup encryption key rotation helpers
- [ ] Multi-repo support (backup to multiple destinations)

---

**Built with ❤️ by [Ranas Mukminov](https://run-as-daemon.ru)**  
**License:** Apache-2.0 | **Language:** Python 3.11+
