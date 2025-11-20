"""Retention policy calculation and enforcement."""

from datetime import datetime, timedelta
from typing import Dict, List

from backup_orchestrator_observability.backends.base import Snapshot
from backup_orchestrator_observability.config import RetentionPolicy


class RetentionCalculator:
    """Calculate which snapshots to keep based on retention policy."""

    @staticmethod
    def get_snapshots_to_keep(
        snapshots: List[Snapshot], policy: RetentionPolicy
    ) -> List[Snapshot]:
        """Determine which snapshots to keep based on retention policy.

        Args:
            snapshots: List of available snapshots (sorted by timestamp desc)
            policy: Retention policy to apply

        Returns:
            List of snapshots that should be kept
        """
        if not snapshots:
            return []

        # Sort snapshots by timestamp (newest first)
        sorted_snaps = sorted(snapshots, key=lambda s: s.timestamp, reverse=True)

        keep_ids = set()

        # Keep last N snapshots
        if policy.keep_last:
            for snap in sorted_snaps[: policy.keep_last]:
                keep_ids.add(snap.id)

        # Bucket-based retention (hourly, daily, weekly, monthly, yearly)
        now = datetime.utcnow()

        if policy.keep_hourly:
            keep_ids.update(
                RetentionCalculator._get_hourly(sorted_snaps, policy.keep_hourly, now)
            )

        if policy.keep_daily:
            keep_ids.update(
                RetentionCalculator._get_daily(sorted_snaps, policy.keep_daily, now)
            )

        if policy.keep_weekly:
            keep_ids.update(
                RetentionCalculator._get_weekly(sorted_snaps, policy.keep_weekly, now)
            )

        if policy.keep_monthly:
            keep_ids.update(
                RetentionCalculator._get_monthly(sorted_snaps, policy.keep_monthly, now)
            )

        if policy.keep_yearly:
            keep_ids.update(
                RetentionCalculator._get_yearly(sorted_snaps, policy.keep_yearly, now)
            )

        # Return snapshots that are in the keep set
        return [snap for snap in snapshots if snap.id in keep_ids]

    @staticmethod
    def _get_hourly(snapshots: List[Snapshot], count: int, now: datetime) -> set:
        """Get IDs of snapshots to keep for hourly retention.

        Args:
            snapshots: Sorted snapshots
            count: Number of hourly snapshots to keep
            now: Current time

        Returns:
            Set of snapshot IDs to keep
        """
        return RetentionCalculator._get_bucketed(
            snapshots, count, now, lambda dt: dt.strftime("%Y%m%d%H")
        )

    @staticmethod
    def _get_daily(snapshots: List[Snapshot], count: int, now: datetime) -> set:
        """Get IDs of snapshots to keep for daily retention."""
        return RetentionCalculator._get_bucketed(
            snapshots, count, now, lambda dt: dt.strftime("%Y%m%d")
        )

    @staticmethod
    def _get_weekly(snapshots: List[Snapshot], count: int, now: datetime) -> set:
        """Get IDs of snapshots to keep for weekly retention."""
        return RetentionCalculator._get_bucketed(
            snapshots, count, now, lambda dt: dt.strftime("%Y%W")
        )

    @staticmethod
    def _get_monthly(snapshots: List[Snapshot], count: int, now: datetime) -> set:
        """Get IDs of snapshots to keep for monthly retention."""
        return RetentionCalculator._get_bucketed(
            snapshots, count, now, lambda dt: dt.strftime("%Y%m")
        )

    @staticmethod
    def _get_yearly(snapshots: List[Snapshot], count: int, now: datetime) -> set:
        """Get IDs of snapshots to keep for yearly retention."""
        return RetentionCalculator._get_bucketed(
            snapshots, count, now, lambda dt: dt.strftime("%Y")
        )

    @staticmethod
    def _get_bucketed(
        snapshots: List[Snapshot], count: int, now: datetime, bucket_fn
    ) -> set:
        """Generic bucketed retention.

        Args:
            snapshots: Sorted snapshots
            count: Number of buckets to keep
            now: Current time
            bucket_fn: Function to convert datetime to bucket key

        Returns:
            Set of snapshot IDs to keep
        """
        buckets: Dict[str, Snapshot] = {}

        for snap in snapshots:
            bucket_key = bucket_fn(snap.timestamp)

            # Keep the newest snapshot in each bucket
            if bucket_key not in buckets:
                buckets[bucket_key] = snap

        # Sort buckets by key (newest first) and take first 'count'
        sorted_buckets = sorted(buckets.items(), key=lambda x: x[0], reverse=True)
        kept_snapshots = [snap for _, snap in sorted_buckets[:count]]

        return {snap.id for snap in kept_snapshots}


def get_snapshots_to_delete(
    snapshots: List[Snapshot], policy: RetentionPolicy
) -> List[Snapshot]:
    """Get list of snapshots that should be deleted based on retention policy.

    Args:
        snapshots: All available snapshots
        policy: Retention policy

    Returns:
        List of snapshots to delete
    """
    keep = RetentionCalculator.get_snapshots_to_keep(snapshots, policy)
    keep_ids = {snap.id for snap in keep}
    return [snap for snap in snapshots if snap.id not in keep_ids]
