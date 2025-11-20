"""Basic unit tests for configuration loading."""

import tempfile
from pathlib import Path

import pytest
import yaml
from backup_orchestrator_observability.config import (
    BackendType,
    BackupJobConfig,
    OrchestratorConfig,
    RetentionPolicy,
    load_config,
)


def test_load_valid_config():
    """Test loading a valid configuration file."""
    config_data = {
        "jobs": [
            {
                "name": "test-job",
                "backend": "restic",
                "sources": ["/home/user/data"],
                "repository": "/mnt/backup/restic",
                "schedule": "0 2 * * *",
                "retention": {
                    "keep_daily": 7,
                    "keep_weekly": 4,
                },
                "rpo_hours": 24,
            }
        ],
        "metrics": {
            "enabled": True,
            "port": 9090,
        },
        "log_level": "INFO",
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.safe_dump(config_data, f)
        config_path = f.name

    try:
        config = load_config(config_path)

        assert len(config.jobs) == 1
        assert config.jobs[0].name == "test-job"
        assert config.jobs[0].backend == BackendType.RESTIC
        assert config.jobs[0].sources == ["/home/user/data"]
        assert config.jobs[0].retention.keep_daily == 7
        assert config.metrics.port == 9090

    finally:
        Path(config_path).unlink()


def test_config_validation_unique_names():
    """Test that job names must be unique."""
    with pytest.raises(ValueError, match="Job names must be unique"):
        OrchestratorConfig(
            jobs=[
                BackupJobConfig(
                    name="duplicate",
                    backend=BackendType.RESTIC,
                    sources=["/data"],
                    repository="/backup",
                    schedule="0 2 * * *",
                ),
                BackupJobConfig(
                    name="duplicate",
                    backend=BackendType.BORG,
                    sources=["/other"],
                    repository="/backup2",
                    schedule="0 3 * * *",
                ),
            ]
        )


def test_config_validation_empty_sources():
    """Test that sources list cannot be empty."""
    with pytest.raises(ValueError, match="At least one source path must be specified"):
        BackupJobConfig(
            name="test",
            backend=BackendType.RESTIC,
            sources=[],
            repository="/backup",
            schedule="0 2 * * *",
        )


def test_retention_policy_validation():
    """Test retention policy validation."""
    # Valid retention
    policy = RetentionPolicy(keep_daily=7, keep_weekly=4)
    assert policy.keep_daily == 7
    assert policy.keep_weekly == 4

    # Invalid: negative values
    with pytest.raises(ValueError):
        RetentionPolicy(keep_daily=-1)


def test_cron_schedule_validation():
    """Test cron schedule validation."""
    # Valid cron expressions
    valid_schedules = [
        "0 2 * * *",  # 5 parts
        "0 0 2 * * *",  # 6 parts (with seconds)
    ]

    for schedule in valid_schedules:
        job = BackupJobConfig(
            name="test",
            backend=BackendType.RESTIC,
            sources=["/data"],
            repository="/backup",
            schedule=schedule,
        )
        assert job.schedule == schedule

    # Invalid cron expression
    with pytest.raises(ValueError, match="Invalid cron expression"):
        BackupJobConfig(
            name="test",
            backend=BackendType.RESTIC,
            sources=["/data"],
            repository="/backup",
            schedule="invalid cron",
        )
