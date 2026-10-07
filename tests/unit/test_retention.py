"""Tests for retention policy calculation."""

from datetime import UTC, datetime, timedelta

from backup_orchestrator_observability.backends.base import Snapshot
from backup_orchestrator_observability.config import BackupJobConfig, RetentionPolicy
from backup_orchestrator_observability.retention import get_snapshots_to_delete


def _snap(snap_id: str, ts: datetime) -> Snapshot:
    return Snapshot(id=snap_id, timestamp=ts, hostname="host", paths=["/data"])


def _daily_snaps(count: int) -> list[Snapshot]:
    base = datetime(2026, 1, 10, 12, tzinfo=UTC)
    return [_snap(f"s{i}", base - timedelta(days=i)) for i in range(count)]


def test_empty_policy_deletes_nothing() -> None:
    assert get_snapshots_to_delete(_daily_snaps(5), RetentionPolicy()) == []


def test_default_job_retention_deletes_nothing() -> None:
    job = BackupJobConfig(
        name="job",
        backend="restic",
        sources=["/data"],
        repository="/repo",
        schedule="0 * * * *",
    )
    assert get_snapshots_to_delete(_daily_snaps(5), job.retention) == []


def test_zero_values_are_treated_as_unset() -> None:
    assert get_snapshots_to_delete(_daily_snaps(5), RetentionPolicy(keep_last=0)) == []


def test_keep_last() -> None:
    deleted = get_snapshots_to_delete(_daily_snaps(5), RetentionPolicy(keep_last=2))
    assert [s.id for s in deleted] == ["s2", "s3", "s4"]


def test_weekly_uses_iso_weeks_across_new_year() -> None:
    # Mon 2025-12-29 .. Sun 2026-01-04 is ISO week 2026-W01.
    snaps = [
        _snap("sat-jan3", datetime(2026, 1, 3, 12, tzinfo=UTC)),
        _snap("thu-jan1", datetime(2026, 1, 1, 12, tzinfo=UTC)),
        _snap("mon-dec29", datetime(2025, 12, 29, 12, tzinfo=UTC)),
        _snap("mon-dec22", datetime(2025, 12, 22, 12, tzinfo=UTC)),  # 2025-W52
    ]
    deleted = get_snapshots_to_delete(snaps, RetentionPolicy(keep_weekly=2))
    assert sorted(s.id for s in deleted) == ["mon-dec29", "thu-jan1"]
