"""Unit tests for RTO/RPO calculation."""

from datetime import datetime, timedelta

import pytest
from backup_disaster_drill_lab.metrics import (
    DrillMetrics,
    assess_drill_success,
    calculate_rpo,
    calculate_rto,
)


def test_calculate_rto():
    """Test RTO calculation."""
    failure_time = datetime(2024, 1, 1, 12, 0, 0)
    recovery_time = datetime(2024, 1, 1, 12, 30, 0)

    rto = calculate_rto(failure_time, recovery_time)

    assert rto == timedelta(minutes=30)
    assert rto.total_seconds() == 1800


def test_calculate_rto_invalid():
    """Test RTO calculation with invalid times."""
    failure_time = datetime(2024, 1, 1, 12, 0, 0)
    recovery_time = datetime(2024, 1, 1, 11, 0, 0)  # Before failure

    with pytest.raises(ValueError, match="Recovery time cannot be before failure time"):
        calculate_rto(failure_time, recovery_time)


def test_calculate_rpo():
    """Test RPO calculation."""
    last_backup = datetime(2024, 1, 1, 2, 0, 0)
    failure_time = datetime(2024, 1, 1, 12, 0, 0)

    rpo = calculate_rpo(failure_time, last_backup)

    assert rpo == timedelta(hours=10)
    assert rpo.total_seconds() == 36000


def test_calculate_rpo_invalid():
    """Test RPO calculation with invalid times."""
    last_backup = datetime(2024, 1, 1, 12, 0, 0)
    failure_time = datetime(2024, 1, 1, 11, 0, 0)  # Before last backup

    with pytest.raises(ValueError, match="Last backup time cannot be after failure time"):
        calculate_rpo(failure_time, last_backup)


def test_assess_drill_success_all_pass():
    """Test drill assessment when all criteria pass."""
    metrics = DrillMetrics(
        rto_seconds=1500,  # 25 minutes
        rpo_seconds=3000,  # 50 minutes
        backup_size_bytes=1024 * 1024 * 1024,  # 1 GB
        restore_duration_seconds=1400,
        verification_success=True,
        data_loss_detected=False,
        metadata={},
    )

    target_rto = 1800  # 30 minutes
    target_rpo = 3600  # 60 minutes

    success, issues = assess_drill_success(metrics, target_rto, target_rpo)

    assert success is True
    assert len(issues) == 0


def test_assess_drill_success_rto_exceeded():
    """Test drill assessment when RTO is exceeded."""
    metrics = DrillMetrics(
        rto_seconds=2000,  # 33 minutes
        rpo_seconds=3000,
        backup_size_bytes=1024 * 1024 * 1024,
        restore_duration_seconds=1900,
        verification_success=True,
        data_loss_detected=False,
        metadata={},
    )

    target_rto = 1800  # 30 minutes
    target_rpo = 3600

    success, issues = assess_drill_success(metrics, target_rto, target_rpo)

    assert success is False
    assert len(issues) == 1
    assert "RTO exceeded target" in issues[0]


def test_assess_drill_success_verification_failed():
    """Test drill assessment when verification fails."""
    metrics = DrillMetrics(
        rto_seconds=1500,
        rpo_seconds=3000,
        backup_size_bytes=1024 * 1024 * 1024,
        restore_duration_seconds=1400,
        verification_success=False,  # Verification failed
        data_loss_detected=False,
        metadata={},
    )

    target_rto = 1800
    target_rpo = 3600

    success, issues = assess_drill_success(metrics, target_rto, target_rpo)

    assert success is False
    assert len(issues) == 1
    assert "Verification failed" in issues[0]


def test_assess_drill_success_data_loss():
    """Test drill assessment when data loss is detected."""
    metrics = DrillMetrics(
        rto_seconds=1500,
        rpo_seconds=3000,
        backup_size_bytes=1024 * 1024 * 1024,
        restore_duration_seconds=1400,
        verification_success=True,
        data_loss_detected=True,  # Data loss detected
        metadata={},
    )

    target_rto = 1800
    target_rpo = 3600

    success, issues = assess_drill_success(metrics, target_rto, target_rpo)

    assert success is False
    assert "Data loss detected" in issues[0]


def test_assess_drill_success_multiple_failures():
    """Test drill assessment with multiple failure conditions."""
    metrics = DrillMetrics(
        rto_seconds=2000,  # RTO exceeded
        rpo_seconds=4000,  # RPO exceeded
        backup_size_bytes=1024 * 1024 * 1024,
        restore_duration_seconds=1900,
        verification_success=False,  # Verification failed
        data_loss_detected=True,  # Data loss
        metadata={},
    )

    target_rto = 1800
    target_rpo = 3600

    success, issues = assess_drill_success(metrics, target_rto, target_rpo)

    assert success is False
    assert len(issues) == 4  # All conditions failed
