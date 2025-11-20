"""Configuration models and loaders for backup orchestrator."""

from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator


class BackendType(str, Enum):
    """Supported backup backend types."""

    RESTIC = "restic"
    BORG = "borg"
    ZFS = "zfs"


class RetentionPolicy(BaseModel):
    """Retention policy for backups."""

    keep_last: int | None = Field(None, description="Keep last N backups")
    keep_hourly: int | None = Field(None, description="Keep N hourly backups")
    keep_daily: int | None = Field(None, description="Keep N daily backups")
    keep_weekly: int | None = Field(None, description="Keep N weekly backups")
    keep_monthly: int | None = Field(None, description="Keep N monthly backups")
    keep_yearly: int | None = Field(None, description="Keep N yearly backups")

    @field_validator("*", mode="before")
    @classmethod
    def validate_positive(cls, v: Any) -> Any:
        """Ensure all retention values are positive."""
        if v is not None and isinstance(v, int) and v < 0:
            raise ValueError("Retention values must be positive integers")
        return v


class BackupJobConfig(BaseModel):
    """Configuration for a single backup job."""

    name: str = Field(..., description="Unique job name")
    backend: BackendType = Field(..., description="Backup backend type")
    sources: list[str] = Field(..., description="Source paths to backup")
    repository: str = Field(..., description="Backup repository location")
    schedule: str = Field(..., description="Cron schedule expression")
    retention: RetentionPolicy = Field(
        default_factory=RetentionPolicy.model_construct, description="Retention policy"
    )
    backend_options: dict[str, Any] = Field(
        default_factory=dict, description="Backend-specific options"
    )
    verification_schedule: str | None = Field(
        None, description="Verification cron schedule (optional)"
    )
    rpo_hours: int = Field(24, description="Recovery Point Objective in hours")
    enabled: bool = Field(True, description="Whether job is enabled")

    @field_validator("sources")
    @classmethod
    def validate_sources(cls, v: list[str]) -> list[str]:
        """Validate that sources list is not empty."""
        if not v:
            raise ValueError("At least one source path must be specified")
        return v

    @field_validator("schedule", "verification_schedule")
    @classmethod
    def validate_cron(cls, v: str | None) -> str | None:
        """Basic cron expression validation."""
        if v is None:
            return v
        parts = v.split()
        if len(parts) not in (5, 6):  # standard cron or with seconds
            raise ValueError(f"Invalid cron expression '{v}': must have 5 or 6 parts")
        return v


class MetricsConfig(BaseModel):
    """Metrics exporter configuration."""

    enabled: bool = Field(True, description="Enable metrics export")
    port: int = Field(9090, description="HTTP metrics port")
    textfile_path: str | None = Field(None, description="Path for textfile collector")


class OrchestratorConfig(BaseModel):
    """Main orchestrator configuration."""

    jobs: list[BackupJobConfig] = Field(..., description="List of backup jobs")
    metrics: MetricsConfig = Field(
        default_factory=MetricsConfig.model_construct, description="Metrics configuration"
    )
    log_level: str = Field("INFO", description="Logging level")
    scheduler_timezone: str = Field("UTC", description="Scheduler timezone")

    @field_validator("jobs")
    @classmethod
    def validate_unique_names(cls, v: list[BackupJobConfig]) -> list[BackupJobConfig]:
        """Ensure all job names are unique."""
        names = [job.name for job in v]
        if len(names) != len(set(names)):
            raise ValueError("Job names must be unique")
        return v


def load_config(config_path: str | Path) -> OrchestratorConfig:
    """Load orchestrator configuration from YAML file.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        Parsed and validated OrchestratorConfig

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML is invalid
        pydantic.ValidationError: If config validation fails
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return OrchestratorConfig.model_validate(data)


def save_config(config: OrchestratorConfig, config_path: str | Path) -> None:
    """Save orchestrator configuration to YAML file.

    Args:
        config: OrchestratorConfig instance
        config_path: Path to save YAML configuration
    """
    path = Path(config_path)
    data = config.model_dump(mode="json", exclude_none=True)

    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
