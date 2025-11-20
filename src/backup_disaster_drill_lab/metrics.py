"""RTO/RPO calculation for disaster recovery drills."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class DrillMetrics:
    """Metrics collected from a disaster recovery drill."""

    rto_seconds: float  # Recovery Time Objective (actual time taken)
    rpo_seconds: float  # Recovery Point Objective (data loss window)
    backup_size_bytes: int
    restore_duration_seconds: float
    verification_success: bool
    data_loss_detected: bool
    metadata: dict


def calculate_rto(failure_time: datetime, recovery_time: datetime) -> timedelta:
    """Calculate Recovery Time Objective.

    RTO is the time between when the failure was detected/injected and when
    the service was fully restored and operational.

    Args:
        failure_time: When the failure occurred or was injected
        recovery_time: When the service was fully restored

    Returns:
        Time delta representing the RTO

    Raises:
        ValueError: If recovery_time is before failure_time
    """
    if recovery_time < failure_time:
        raise ValueError("Recovery time cannot be before failure time")

    return recovery_time - failure_time


def calculate_rpo(failure_time: datetime, last_backup_time: datetime) -> timedelta:
    """Calculate Recovery Point Objective.

    RPO is the time between the last successful backup and the failure,
    representing the potential window of data loss.

    Args:
        failure_time: When the failure occurred
        last_backup_time: When the most recent backup completed

    Returns:
        Time delta representing the RPO

    Raises:
        ValueError: If last_backup_time is after failure_time
    """
    if last_backup_time > failure_time:
        raise ValueError("Last backup time cannot be after failure time")

    return failure_time - last_backup_time


def assess_drill_success(
    metrics: DrillMetrics,
    target_rto_seconds: float,
    target_rpo_seconds: float,
) -> tuple[bool, list[str]]:
    """Assess whether a drill met success criteria.

    Args:
        metrics: Drill metrics
        target_rto_seconds: Target RTO threshold
        target_rpo_seconds: Target RPO threshold

    Returns:
        Tuple of (success, list of issues)
    """
    issues = []

    if metrics.rto_seconds > target_rto_seconds:
        issues.append(
            f"RTO exceeded target: {metrics.rto_seconds:.1f}s > {target_rto_seconds:.1f}s"
        )

    if metrics.rpo_seconds > target_rpo_seconds:
        issues.append(
            f"RPO exceeded target: {metrics.rpo_seconds:.1f}s > {target_rpo_seconds:.1f}s"
        )

    if not metrics.verification_success:
        issues.append("Verification failed after restore")

    if metrics.data_loss_detected:
        issues.append("Data loss detected after restore")

    return (len(issues) == 0, issues)
